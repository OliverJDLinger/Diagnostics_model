"""Block 0:"""
"""Hypergraph store package: schema, store, and persistence."""
from .schema import Entity, Hyperedge
from .store import HypergraphStore
from .persistence import save_hypergraph, load_hypergraph

__all__ = [
    "Entity",
    "Hyperedge",
    "HypergraphStore",
    "save_hypergraph",
    "load_hypergraph",
]