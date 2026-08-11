"""Round-trip and invariant tests for the hypergraph store (Block 0 validation)."""
from __future__ import annotations

import pytest

from hypergraph import (
    Entity,
    Hyperedge,
    HypergraphStore,
    save_hypergraph,
    load_hypergraph,
)


def build_sample_store() -> HypergraphStore:
    store = HypergraphStore()
    for eid, name in [
        ("drug_aspirin", "Aspirin"),
        ("cond_headache", "Headache"),
        ("dose_300mg", "300 mg"),
        ("cond_ulcer", "Peptic ulcer"),
    ]:
        store.add_entity(Entity(id=eid, name=name))
    store.add_hyperedge(
        Hyperedge(
            id="he_0001",
            relation="treats",
            roles={"agent": "drug_aspirin", "target": "cond_headache", "dose": "dose_300mg"},
        )
    )
    store.add_hyperedge(
        Hyperedge(
            id="he_0002",
            relation="contraindicated_in",
            roles={"agent": "drug_aspirin", "target": "cond_ulcer"},
        )
    )
    return store


def test_add_and_get():
    store = build_sample_store()
    assert len(store) == 2
    assert store.get_hyperedge("he_0001").relation == "treats"
    assert store.get_hyperedge("he_0001").entity_ids == {
        "drug_aspirin",
        "cond_headache",
        "dose_300mg",
    }


def test_incident_edges_sorted():
    store = build_sample_store()
    incident = store.hyperedges_incident_to("drug_aspirin")
    assert [h.id for h in incident] == ["he_0001", "he_0002"]


def test_unknown_entity_raises():
    store = HypergraphStore()
    store.add_entity(Entity("a", "A"))
    with pytest.raises(ValueError):
        store.add_hyperedge(Hyperedge("he_x", "rel", {"r1": "a", "r2": "missing"}))


def test_repeated_entity_raises_by_default():
    store = HypergraphStore()
    store.add_entity(Entity("a", "A"))
    with pytest.raises(ValueError):
        store.add_hyperedge(Hyperedge("he_x", "rel", {"r1": "a", "r2": "a"}))


def test_repeated_entity_allowed_when_configured():
    store = HypergraphStore(allow_repeated_entity=True)
    store.add_entity(Entity("a", "A"))
    store.add_hyperedge(Hyperedge("he_x", "self_rel", {"r1": "a", "r2": "a"}))
    assert len(store) == 1


def test_relation_required():
    with pytest.raises(ValueError):
        Hyperedge("he_x", "", {"r1": "a", "r2": "b"})


def test_min_two_entities():
    with pytest.raises(ValueError):
        Hyperedge("he_x", "rel", {"only": "a"})


def test_deterministic_iteration():
    store = build_sample_store()
    ids = [h.id for h in store.iter_hyperedges()]
    assert ids == sorted(ids)


def test_round_trip(tmp_path):
    store = build_sample_store()
    path = tmp_path / "hg.json"
    save_hypergraph(store, path)
    reloaded = load_hypergraph(path)
    assert reloaded.to_dict() == store.to_dict()

