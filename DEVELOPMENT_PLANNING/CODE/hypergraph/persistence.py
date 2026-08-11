from __future__ import annotations
"""Block 0:"""
"""Persistence for the hypergraph store, kept separate from store logic.

The store does not know where its data comes from; these helpers do. (Named
``persistence`` rather than ``io`` to avoid shadowing the stdlib ``io`` module.)
This file is responsible for taking the JSON and reading/writing it to disk. 
"""

import json
from pathlib import Path

from .store import HypergraphStore

#Store the data for the hypergraph in a JSON file. 
# The store is converted to a dictionary and then serialized to JSON with stable ordering for reproducible diffs. 
def save_hypergraph(store: HypergraphStore, path) -> None:
    """Write the store to JSON (stable ordering for reproducible diffs)."""
    Path(path).write_text(
        json.dumps(store.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )


# The load function reads the JSON file and reconstructs the HypergraphStore from the dictionary representation.
def load_hypergraph(path) -> HypergraphStore:
    """Rebuild a store from a JSON file written by save_hypergraph."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return HypergraphStore.from_dict(data)