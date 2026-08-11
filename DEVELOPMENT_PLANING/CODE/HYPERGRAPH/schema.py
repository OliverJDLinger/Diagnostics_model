"""Block 0:
Schema for the hypergraph store: Entity and Hyperedge value objects.

Defines *what a fact is*. A Hyperedge is an n-ary, role-typed fact: a relation
label plus a mapping of role -> entity id. Identity is the stable ``id``, which
is the anchor that SAE features and phasors reference downstream. Because the
role mapping is a dict (unhashable), object identity/hashing is keyed on ``id``
only -- which is exactly what we want, since the id is the anchor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, eq=False)
class Entity:
    """A node in the hypergraph.

    Args:
        id: Stable unique identifier (the entity's identity everywhere).
        name: Human-readable label.
        attributes: Optional free-form metadata (immutable after construction).
    """

    id: str
    name: str
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Entity.id is required")
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entity) and other.id == self.id

    def __hash__(self) -> int:
        return hash(("Entity", self.id))


@dataclass(frozen=True, eq=False)
class Hyperedge:
    """An n-ary, role-typed fact.

    Example:
        Hyperedge(
            id="he_0001",
            relation="treats",
            roles={"agent": "drug_x", "target": "cond_y", "dose": "dose_z"},
        )

    Args:
        id: Stable unique identifier; the anchor for concepts/phasors downstream.
        relation: Relation label (required, non-empty).
        roles: Order-by-meaning mapping role -> entity id (>= 2 entries).
        attributes: Optional free-form metadata (immutable after construction).
    """

    id: str
    relation: str
    roles: Mapping[str, str] = field(default_factory=dict)
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Hyperedge.id is required")
        if not self.relation:
            raise ValueError(f"Hyperedge {self.id!r}: relation label is required")
        if len(self.roles) < 2:
            raise ValueError(
                f"Hyperedge {self.id!r}: needs >= 2 role-bound entities, "
                f"got {len(self.roles)}"
            )
        object.__setattr__(self, "roles", MappingProxyType(dict(self.roles)))
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

    @property
    def entity_ids(self) -> set:
        """The set of entity ids referenced by this fact (across all roles)."""
        return set(self.roles.values())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Hyperedge) and other.id == self.id

    def __hash__(self) -> int:
        return hash(("Hyperedge", self.id))