"""Block 0:
In-memory hypergraph store.

Holds Entities and Hyperedges and answers the structural questions the rest of
the pipeline asks: add / get-by-id / edges incident to an entity / deterministic
iteration. Wraps its own storage rather than exposing a backend, so the backend
can change later (e.g. a graph DB) without affecting callers. Which is what the later iterations will require.


Deliberately NON-quantum and NON-retrieval: this layer holds structure only.
"""
from __future__ import annotations

from typing import Dict, Iterator, List, Set

from .schema import Entity, Hyperedge


class HypergraphStore:
    """A small, deterministic, validated hypergraph of role-typed facts.

    Args:
        allow_repeated_entity: If False (default), a hyperedge may not bind the
            same entity to more than one role -- this catches data-entry errors.
            Set True only if you have genuinely reflexive relations.
    """

    def __init__(self, allow_repeated_entity: bool = False) -> None:
        self._entities: Dict[str, Entity] = {}
        self._hyperedges: Dict[str, Hyperedge] = {}
        self._incidence: Dict[str, Set[str]] = {}  # entity_id -> {hyperedge_id}
        self.allow_repeated_entity = allow_repeated_entity

    # -- entities -----------------------------------------------------------
    def add_entity(self, entity: Entity) -> None:
        """Register an entity. Raises if the id is already present."""
        if entity.id in self._entities:
            raise ValueError(f"Entity id {entity.id!r} already registered")
        self._entities[entity.id] = entity
        self._incidence.setdefault(entity.id, set())

    def get_entity(self, entity_id: str) -> Entity:
        return self._entities[entity_id]

    def has_entity(self, entity_id: str) -> bool:
        return entity_id in self._entities

    # -- hyperedges ---------------------------------------------------------
    def add_hyperedge(self, edge: Hyperedge, auto_add_entities: bool = False) -> None:
        """Add a fact, validating referential integrity.

        Raises:
            ValueError: on duplicate edge id; on an unknown entity (unless
                auto_add_entities=True); or on a repeated entity across roles
                (unless the store was built with allow_repeated_entity=True).
        """
        if edge.id in self._hyperedges:
            raise ValueError(f"Hyperedge id {edge.id!r} already exists")

        entity_ids = list(edge.roles.values())
        if not self.allow_repeated_entity and len(set(entity_ids)) != len(entity_ids):
            raise ValueError(
                f"Hyperedge {edge.id!r}: same entity bound to multiple roles "
                f"(set allow_repeated_entity=True if intended)"
            )

        for eid in entity_ids:
            if eid not in self._entities:
                if auto_add_entities:
                    self.add_entity(Entity(id=eid, name=eid))
                else:
                    raise ValueError(
                        f"Hyperedge {edge.id!r} references unknown entity {eid!r} "
                        f"(add it first, or pass auto_add_entities=True)"
                    )

        self._hyperedges[edge.id] = edge
        for eid in edge.entity_ids:
            self._incidence[eid].add(edge.id)

    def get_hyperedge(self, edge_id: str) -> Hyperedge:
        return self._hyperedges[edge_id]

    def hyperedges_incident_to(self, entity_id: str) -> List[Hyperedge]:
        """All facts touching an entity, sorted by hyperedge id (deterministic)."""
        if entity_id not in self._entities:
            raise KeyError(entity_id)
        return [self._hyperedges[hid] for hid in sorted(self._incidence[entity_id])]

    # -- iteration / size ---------------------------------------------------
    def iter_hyperedges(self) -> Iterator[Hyperedge]:
        """Iterate hyperedges in stable order (sorted by id) for reproducibility."""
        for hid in sorted(self._hyperedges):
            yield self._hyperedges[hid]

    def iter_entities(self) -> Iterator[Entity]:
        for eid in sorted(self._entities):
            yield self._entities[eid]

    def __len__(self) -> int:
        return len(self._hyperedges)

    def __contains__(self, edge_id: object) -> bool:
        return edge_id in self._hyperedges

    # -- serialization ------------------------------------------------------
    def to_dict(self) -> dict:
        """Plain-dict representation (JSON-serialisable), deterministic ordering."""
        return {
            "allow_repeated_entity": self.allow_repeated_entity,
            "entities": [
                {"id": e.id, "name": e.name, "attributes": dict(e.attributes)}
                for e in self.iter_entities()
            ],
            "hyperedges": [
                {
                    "id": h.id,
                    "relation": h.relation,
                    "roles": dict(h.roles),
                    "attributes": dict(h.attributes),
                }
                for h in self.iter_hyperedges()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HypergraphStore":
        store = cls(allow_repeated_entity=data.get("allow_repeated_entity", False))
        for e in data.get("entities", []):
            store.add_entity(
                Entity(id=e["id"], name=e["name"], attributes=e.get("attributes", {}))
            )
        for h in data.get("hyperedges", []):
            store.add_hyperedge(
                Hyperedge(
                    id=h["id"],
                    relation=h["relation"],
                    roles=h["roles"],
                    attributes=h.get("attributes", {}),
                )
            )
        return store