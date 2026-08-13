"""Real-valued baseline encoder (TransE-style). The NON-quantum arm.

Role acts by translation, distance is L2. No phase -- so there is no
encode-to-state here: a real vector is not a quantum state and there is nothing
for the walk to evolve. This file exists to keep the baseline cleanly separate
from the complex arm.
"""
from __future__ import annotations

from typing import Sequence, Tuple

import torch
import torch.nn as nn

from .base_encoder import BaseEncoder


class RealEncoder(BaseEncoder):
    """TransE-style baseline: role = translation, distance = L2."""

    def __init__(self, num_entities: int, num_relations: int, num_roles: int, dim: int = 32) -> None:
        super().__init__()
        self.dim = dim
        self.mode = "real"
        self.ent = nn.Embedding(num_entities, dim)
        self.rel = nn.Embedding(num_relations, dim)
        self.role = nn.Embedding(num_roles, dim)  # translation vector
        for emb in (self.ent, self.rel, self.role):
            nn.init.uniform_(emb.weight, -0.1, 0.1)

    def score_fact(self, relation: int, roles: Sequence[Tuple[int, int]]) -> torch.Tensor:
        rel_id, role_ids, ent_ids = self._ids(relation, roles)
        placed = self.ent(ent_ids) + self.role(role_ids)   # role = translation
        agg = placed.mean(dim=0)                            # INVARIANT: mean over roles
        return torch.linalg.vector_norm(agg - self.rel(rel_id), ord=2)