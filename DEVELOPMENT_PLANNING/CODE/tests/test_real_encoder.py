"""Tests for the real (baseline) encoder arm."""
from __future__ import annotations

import torch

from hypergraph import Entity, Hyperedge, HypergraphStore
from embeddings import Vocabulary
from embeddings.real_encoder import RealEncoder


def build_vocab() -> Vocabulary:
    store = HypergraphStore()
    for eid, name in [("drug_aspirin", "Aspirin"), ("cond_headache", "Headache"),
                      ("dose_300mg", "300 mg"), ("cond_ulcer", "Peptic ulcer")]:
        store.add_entity(Entity(id=eid, name=name))
    store.add_hyperedge(Hyperedge(id="he_0001", relation="treats",
        roles={"agent": "drug_aspirin", "target": "cond_headache", "dose": "dose_300mg"}))
    store.add_hyperedge(Hyperedge(id="he_0002", relation="contraindicated_in",
        roles={"agent": "drug_aspirin", "target": "cond_ulcer"}))
    return Vocabulary(store)


def make(dim=8):
    torch.manual_seed(0)
    v = build_vocab()
    return v, RealEncoder(v.num_entities, v.num_relations, v.num_roles, dim=dim)


def test_scores_shape_nonneg():
    v, m = make()
    s = m(v.facts())
    assert s.shape == (len(v),)
    assert torch.all(s >= 0)


def test_real_arm_has_no_state_handoff():
    # The baseline has no phase, so it must NOT expose encode_state.
    _, m = make()
    assert not hasattr(m, "encode_state")


def test_deterministic():
    a = make()[1](build_vocab().facts())
    b = make()[1](build_vocab().facts())
    assert torch.allclose(a, b)