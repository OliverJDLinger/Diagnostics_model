"""Continuous-time quantum walk over the hypergraph (Phase: evolution layer).

The rigorous version of "encode into Hilbert space, apply the Schrodinger
equation, watch concepts move without degrading."

Pipeline of the maths (hbar = 1):
    encode:  |psi> = v / ||v||            (unit state; |psi_i|^2 is a probability)
    evolve:  i d|psi>/dt = H|psi|  =>  |psi(t)> = e^{-iHt} |psi(0)>
    theorem: H = H^dagger  =>  e^{-iHt} is unitary  =>  ||psi(t)|| = 1  for all t

So if H is Hermitian, non-degradation is guaranteed -- it is what "unitary"
means. Under this evolution the state does not shrink, it ROTATES: magnitudes
conserved, phases turning. That turning IS the concept drift. 

The state space is the graph's entities (nodes). A localized start (one-hot on a
concept) spreads amplitude along the graph's connections over time -- a concept
walking through the knowledge structure.
"""
from __future__ import annotations

import numpy as np

from hypergraph import HypergraphStore


def entity_adjacency(store: HypergraphStore, entity2id: dict) -> np.ndarray:
    """Symmetric co-occurrence adjacency over entities.

    A[i, j] = number of hyperedges containing BOTH entity i and entity j.
    Symmetric by construction, so it is a valid (real) Hermitian operator.
    """
    n = len(entity2id)
    A = np.zeros((n, n), dtype=float)
    for h in store.iter_hyperedges():
        ids = [entity2id[e] for e in h.entity_ids]
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                i, j = ids[a], ids[b]
                A[i, j] += 1.0
                A[j, i] += 1.0
    return A


def hamiltonian(store: HypergraphStore, entity2id: dict, kind: str = "adjacency") -> np.ndarray:
    """Build a Hermitian Hamiltonian from the hypergraph structure.

    kind="adjacency": H = A  (amplitude hops between co-occurring concepts).
    kind="laplacian": H = D - A  (diffusion-style generator).
    Both are real symmetric, hence Hermitian, hence generate unitary evolution.
    """
    A = entity_adjacency(store, entity2id)
    if kind == "adjacency":
        H = A
    elif kind == "laplacian":
        H = np.diag(A.sum(axis=1)) - A
    else:
        raise ValueError(f"kind must be 'adjacency' or 'laplacian', got {kind!r}")
    assert np.allclose(H, H.conj().T), "Hamiltonian must be Hermitian"
    return H


def normalise(v) -> np.ndarray:
    """Turn any nonzero vector into a unit-norm quantum state."""
    v = np.asarray(v, dtype=complex)
    norm = np.linalg.norm(v)
    if norm == 0:
        raise ValueError("zero vector cannot be normalised to a state")
    return v / norm


def one_hot_state(entity_index: int, n: int) -> np.ndarray:
    """A state fully localized on one concept (start of a walk)."""
    psi = np.zeros(n, dtype=complex)
    psi[entity_index] = 1.0
    return psi


class QuantumWalk:
    """Exact unitary evolution under a Hermitian H, via eigendecomposition.

    We diagonalise once: H = V diag(lambda) V^dagger, then
        e^{-iHt} |psi> = V e^{-i lambda t} V^dagger |psi>,
    which is the EXACT propagator -- not a discretised step -- so the norm is
    preserved to machine precision at any t.
    """

    def __init__(self, H: np.ndarray) -> None:
        H = np.asarray(H, dtype=complex)
        if not np.allclose(H, H.conj().T):
            raise ValueError("H must be Hermitian for unitary evolution")
        self.H = H
        # eigh is for Hermitian matrices: real eigenvalues, orthonormal eigenvectors.
        self.eigenvalues, self.eigenvectors = np.linalg.eigh(H)

    def evolve(self, psi0, t: float) -> np.ndarray:
        """Return |psi(t)> = e^{-iHt} |psi0> (psi0 is normalised first)."""
        psi0 = normalise(psi0)
        coeffs = self.eigenvectors.conj().T @ psi0          # project onto eigenbasis
        phased = np.exp(-1j * self.eigenvalues * t) * coeffs  # rotate each eigenmode
        return self.eigenvectors @ phased                    # back to concept basis

    def trajectory(self, psi0, times) -> np.ndarray:
        """States at each t. Returns a (len(times), n) complex array."""
        return np.stack([self.evolve(psi0, t) for t in times])


# -- readouts (what the visualiser will plot) -------------------------------
def probabilities(states: np.ndarray) -> np.ndarray:
    """Born rule: |psi_i|^2 per concept (rows sum to 1)."""
    return np.abs(states) ** 2


def phases(states: np.ndarray) -> np.ndarray:
    """arg(psi_i) per concept -- the angle the visualiser plots."""
    return np.angle(states)


def relative_phase(states: np.ndarray, i: int, j: int) -> np.ndarray:
    """Relative phase between concepts i and j over time (the drift signal)."""
    return np.angle(states[:, i]) - np.angle(states[:, j])


def norms(states: np.ndarray) -> np.ndarray:
    """||psi(t)|| at each step -- should stay 1.0 (the non-degradation check)."""
    return np.linalg.norm(states, axis=1)


# -- contrast: the WRONG way, to show why we use the exact exponential ------
def euler_step(H: np.ndarray, psi: np.ndarray, dt: float) -> np.ndarray:
    """Naive forward-Euler step: psi - i H psi dt. NOT unitary -- the norm
    drifts. Provided only to demonstrate the trap; do not use for real runs."""
    return psi - 1j * (H @ psi) * dt