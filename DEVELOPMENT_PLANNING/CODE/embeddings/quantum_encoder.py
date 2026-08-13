"""Complex ("quantum-inspired") encoder (RotatE-style). The complex arm.

Role acts by rotation, distance is measured in C. Each embedding dimension is a
phasor (real + imaginary part) with a magnitude and a phase. This arm also
supplies encode_fact/encode_state -- the hand-off that turns a concept into a
unit quantum state |psi(0)> for the quantum walk.
"""
from __future__ import annotations

import math
from typing import Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn

from .base_encoder import BaseEncoder


class QuantumEncoder(BaseEncoder):
    """RotatE-style complex arm: role = rotation, distance in C."""

    def __init__(self, num_entities: int, num_relations: int, num_roles: int, dim: int = 32) -> None:
        super().__init__()
        self.dim = dim
        self.mode = "complex"
        # Entity: d free phasors (real & imaginary parts).
        self.ent_re = nn.Embedding(num_entities, dim)
        self.ent_im = nn.Embedding(num_entities, dim)
        # Relation: a target point in complex space.
        self.rel_re = nn.Embedding(num_relations, dim)
        self.rel_im = nn.Embedding(num_relations, dim)
        # Role: a pure rotation per dimension (angle). Unit modulus by construction.
        self.role_phase = nn.Embedding(num_roles, dim)
        for emb in (self.ent_re, self.ent_im, self.rel_re, self.rel_im):
            nn.init.uniform_(emb.weight, -0.1, 0.1)
        nn.init.uniform_(self.role_phase.weight, 0.0, 2 * math.pi)

    def _rotate(self, ent_ids: torch.Tensor, role_ids: torch.Tensor):
        """R_rho e : rotate each entity's phasors by its role angle. Returns (re, im)."""
        er, ei = self.ent_re(ent_ids), self.ent_im(ent_ids)
        theta = self.role_phase(role_ids)
        cos, sin = torch.cos(theta), torch.sin(theta)
        return er * cos - ei * sin, er * sin + ei * cos

    def score_fact(self, relation: int, roles: Sequence[Tuple[int, int]]) -> torch.Tensor:
        rel_id, role_ids, ent_ids = self._ids(relation, roles)
        rot_re, rot_im = self._rotate(ent_ids, role_ids)
        agg_re, agg_im = rot_re.mean(dim=0), rot_im.mean(dim=0)   # INVARIANT: mean over roles
        d_re = agg_re - self.rel_re(rel_id)
        d_im = agg_im - self.rel_im(rel_id)
        return torch.sqrt(d_re ** 2 + d_im ** 2 + 1e-12).sum()

    # -- hand-off to the walk ----------------------------------------------
    def encode_fact(self, roles: Sequence[Tuple[int, int]]) -> np.ndarray:
        """Stage 1: c = (1/k) sum_i R_{rho_i} e_i. Returns complex c of shape (dim,)."""
        role_ids = torch.tensor([r for r, _ in roles], dtype=torch.long)
        ent_ids = torch.tensor([e for _, e in roles], dtype=torch.long)
        with torch.no_grad():
            rot_re, rot_im = self._rotate(ent_ids, role_ids)
            c_re, c_im = rot_re.mean(dim=0), rot_im.mean(dim=0)
        return c_re.numpy() + 1j * c_im.numpy()

    def encode_state(self, roles: Sequence[Tuple[int, int]]) -> np.ndarray:
        """Stage 2: |psi(0)> = c / ||c||. Unit-norm complex state for the walk."""
        c = self.encode_fact(roles)
        norm = np.linalg.norm(c)
        if norm == 0:
            raise ValueError("encoded concept has zero norm; cannot normalise to a state")
        return c / norm