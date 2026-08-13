"""Tests for the quantum-walk evolution layer.

The headline test is norm preservation: it is the 'does not degrade' guarantee,
made to prove itself.
"""
from __future__ import annotations

import numpy as np

from hypergraph import Entity, Hyperedge, HypergraphStore
from embeddings import Vocabulary
from quantum_walk import (
    hamiltonian, one_hot_state, QuantumWalk, probabilities, norms,
    relative_phase, euler_step,
)


def build():
    store = HypergraphStore()
    for eid, name in [
        ("drug_aspirin", "Aspirin"),
        ("cond_headache", "Headache"),
        ("dose_300mg", "300 mg"),
        ("cond_ulcer", "Peptic ulcer"),
    ]:
        store.add_entity(Entity(id=eid, name=name))
    store.add_hyperedge(Hyperedge(id="he_0001", relation="treats",
        roles={"agent": "drug_aspirin", "target": "cond_headache", "dose": "dose_300mg"}))
    store.add_hyperedge(Hyperedge(id="he_0002", relation="contraindicated_in",
        roles={"agent": "drug_aspirin", "target": "cond_ulcer"}))
    vocab = Vocabulary(store)
    H = hamiltonian(store, vocab.entity2id, kind="adjacency")
    return store, vocab, H


def test_hamiltonian_hermitian():
    _, _, H = build()
    assert np.allclose(H, H.conj().T)


def test_norm_preserved_for_all_t():
    # THE key result: unitary evolution does not degrade the state.
    _, vocab, H = build()
    walk = QuantumWalk(H)
    psi0 = one_hot_state(vocab.entity2id["drug_aspirin"], vocab.num_entities)
    times = np.linspace(0, 25, 200)
    states = walk.trajectory(psi0, times)
    assert np.allclose(norms(states), 1.0, atol=1e-10)


def test_probabilities_sum_to_one():
    _, vocab, H = build()
    walk = QuantumWalk(H)
    psi0 = one_hot_state(vocab.entity2id["drug_aspirin"], vocab.num_entities)
    states = walk.trajectory(psi0, np.linspace(0, 10, 50))
    assert np.allclose(probabilities(states).sum(axis=1), 1.0, atol=1e-10)


def test_t0_is_identity():
    _, vocab, H = build()
    walk = QuantumWalk(H)
    psi0 = one_hot_state(vocab.entity2id["drug_aspirin"], vocab.num_entities)
    assert np.allclose(walk.evolve(psi0, 0.0), psi0)


def test_amplitude_spreads_to_connected_concept():
    # Start localized on aspirin; it is connected to headache via he_0001,
    # so probability should leak there over time (a concept walking the graph).
    _, vocab, H = build()
    walk = QuantumWalk(H)
    a = vocab.entity2id["drug_aspirin"]
    h = vocab.entity2id["cond_headache"]
    psi0 = one_hot_state(a, vocab.num_entities)
    states = walk.trajectory(psi0, np.linspace(0, 5, 100))
    p_headache = probabilities(states)[:, h]
    assert p_headache.max() > 0.05  # amplitude genuinely reached headache


def test_reversibility():
    # Unitary => reversible: evolve forward then back recovers the start.
    _, vocab, H = build()
    walk = QuantumWalk(H)
    psi0 = one_hot_state(vocab.entity2id["drug_aspirin"], vocab.num_entities)
    there = walk.evolve(psi0, 3.7)
    back = walk.evolve(there, -3.7)
    assert np.allclose(back, walk.evolve(psi0, 0.0), atol=1e-10)


def test_relative_phase_moves():
    # Drift: the relative phase between two concepts actually changes over time.
    _, vocab, H = build()
    walk = QuantumWalk(H)
    psi0 = np.ones(vocab.num_entities, dtype=complex)  # equal superposition
    states = walk.trajectory(psi0, np.linspace(0, 10, 100))
    a = vocab.entity2id["drug_aspirin"]
    u = vocab.entity2id["cond_ulcer"]
    rp = relative_phase(states, a, u)
    assert rp.std() > 1e-3  # the angle between them genuinely drifts


def test_non_hermitian_rejected():
    bad = np.array([[0, 1], [0, 0]], dtype=complex)  # not Hermitian
    try:
        QuantumWalk(bad)
        assert False, "should have raised"
    except ValueError:
        pass


def test_euler_degrades_norm():
    # The trap: a naive step is NOT unitary, so the norm drifts away from 1.
    _, vocab, H = build()
    psi = one_hot_state(vocab.entity2id["drug_aspirin"], vocab.num_entities).astype(complex)
    for _ in range(500):
        psi = euler_step(H, psi, dt=0.05)
    assert abs(np.linalg.norm(psi) - 1.0) > 0.1  # visibly degraded