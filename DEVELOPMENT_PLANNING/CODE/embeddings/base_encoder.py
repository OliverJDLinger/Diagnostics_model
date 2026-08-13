"""Shared base for the two embedder arms.

forward() and the id-tensor boilerplate live here so both arms are used
identically. Each arm supplies its own tables (__init__) and its own score_fact()
algebra (rotation vs translation).

INVARIANT for the honest baseline: both arms aggregate by 'mean over the
role-placed entities', and compare the aggregate to the relation. Only the
placement op (role o entity) and the distance metric differ between arms.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import torch
import torch.nn as nn


class BaseEncoder(nn.Module):
    def score_fact(self, relation: int, roles: Sequence[Tuple[int, int]]) -> torch.Tensor:
        raise NotImplementedError("subclasses (RealEncoder / QuantumEncoder) implement this")

    def forward(self, facts: List) -> torch.Tensor:
        """Score a list of Facts. Returns a 1-D tensor (one score per fact)."""
        return torch.stack([self.score_fact(f.relation, f.roles) for f in facts])

    @staticmethod
    def _ids(relation: int, roles: Sequence[Tuple[int, int]]):
        """Unpack a fact into (relation_id, role_ids, entity_ids) tensors."""
        role_ids = torch.tensor([r for r, _ in roles], dtype=torch.long)
        ent_ids = torch.tensor([e for _, e in roles], dtype=torch.long)
        rel_id = torch.tensor(relation, dtype=torch.long)
        return rel_id, role_ids, ent_ids