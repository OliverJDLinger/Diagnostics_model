"""Tests for the complex (quantum) encoder arm."""
from __future__ import annotations

import torch

from hypergraph import Entity, Hyperedge, HypergraphStore
from embeddings import Vocabulary
from embeddings.quantum_encoder import QuantumEncoder


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
    return v, QuantumEncoder(v.num_entities, v.num_relations, v.num_roles, dim=dim)


def test_scores_shape_nonneg():
    v, m = make()
    s = m(v.facts())
    assert s.shape == (len(v),)
    assert torch.all(s >= 0)


def test_role_rotation_preserves_magnitude():
    v, m = make(dim=16)
    rot_re, rot_im = m._rotate(torch.tensor([0]), torch.tensor([0]))
    before = torch.sqrt(m.ent_re(torch.tensor([0]))**2 + m.ent_im(torch.tensor([0]))**2)
    after = torch.sqrt(rot_re**2 + rot_im**2)
    assert torch.allclose(before, after, atol=1e-6)


def test_gradients_flow():
    v, m = make()
    m(v.facts()).sum().backward()
    assert m.ent_re.weight.grad is not None and torch.any(m.ent_re.weight.grad != 0)


def test_deterministic():
    a = make()[1](build_vocab().facts())
    b = make()[1](build_vocab().facts())
    assert torch.allclose(a, b)