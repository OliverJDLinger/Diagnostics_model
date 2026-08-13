"""Vocabulary and indexing for the embedding layer.

Maps every entity, relation, and role to a stable integer id, and renders each
hyperedge as an integer-id Fact. Deterministic (ids assigned in sorted order).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from hypergraph import HypergraphStore, Hyperedge


@dataclass(frozen=True)
class Fact:
    edge_id: str
    relation: int
    roles: Tuple[Tuple[int, int], ...]


class Vocabulary:
    def __init__(self, store: HypergraphStore) -> None:
        entities = sorted(e.id for e in store.iter_entities())
        relations = sorted({h.relation for h in store.iter_hyperedges()})
        roles = sorted({r for h in store.iter_hyperedges() for r in h.roles})

        self.entity2id: Dict[str, int] = {t: i for i, t in enumerate(entities)}
        self.relation2id: Dict[str, int] = {t: i for i, t in enumerate(relations)}
        self.role2id: Dict[str, int] = {t: i for i, t in enumerate(roles)}
        self.id2entity = {i: t for t, i in self.entity2id.items()}
        self.id2relation = {i: t for t, i in self.relation2id.items()}
        self.id2role = {i: t for t, i in self.role2id.items()}

        self._facts: List[Fact] = [self._to_fact(h) for h in store.iter_hyperedges()]

    def _to_fact(self, h: Hyperedge) -> Fact:
        roles = tuple(sorted(
            (self.role2id[role], self.entity2id[ent]) for role, ent in h.roles.items()
        ))
        return Fact(edge_id=h.id, relation=self.relation2id[h.relation], roles=roles)

    @property
    def num_entities(self) -> int:
        return len(self.entity2id)

    @property
    def num_relations(self) -> int:
        return len(self.relation2id)

    @property
    def num_roles(self) -> int:
        return len(self.role2id)

    def facts(self) -> List[Fact]:
        return list(self._facts)

    def decode(self, fact: Fact) -> dict:
        return {
            "edge_id": fact.edge_id,
            "relation": self.id2relation[fact.relation],
            "roles": {self.id2role[r]: self.id2entity[e] for r, e in fact.roles},
        }

    def __len__(self) -> int:
        return len(self._facts)