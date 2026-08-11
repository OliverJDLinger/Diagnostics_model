"""Dynamics: evolve concept states over the hypergraph via the Schrodinger
equation (continuous-time quantum walk). Norm-preserving by construction."""
from .quantum_walk import (
    entity_adjacency,
    hamiltonian,
    normalise,
    one_hot_state,
    QuantumWalk,
    probabilities,
    phases,
    relative_phase,
    norms,
    euler_step,
)

__all__ = [
    "entity_adjacency", "hamiltonian", "normalise", "one_hot_state",
    "QuantumWalk", "probabilities", "phases", "relative_phase", "norms",
    "euler_step",
]