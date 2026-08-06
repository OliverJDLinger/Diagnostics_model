# CODE BLOCKS 1: Quantum HyperRAG + sparce autoencoder
Virtual env created name venv-olie
Folder structure (Capitals = folders)
CODE
    DATA
    DOCS
    QUANTUM_HYP 
    VISUALISATION

## Block Criteria
A code block is considered auditable when the following are true:
- Its purpose is explicit
- Its inputs and outputs are documented
- Its dependencies are known
- It has a test or validation step
- Its limitations are stated
- Its review status is recorded

## Block Structure 
- Block name
- Purpose
- Files involved
- Inputs
- Outputs
- Dependencies
- Assumptions
- Test or validation method
- Known limitations
- Review status

### CODE BLOCK [0]
- Block name: HyperGraph Store
- Purpose: store entities as nodes and n-ary facts as hyperedges; the hyperedge is the shared concept unit for later comparison and visualisation
- Phase: 1
- Files: hypergraph/store.py, hypergraph/schema.py
- Inputs: entity list + n-ary facts (each fact = a set of entities + a relation label), as dict/JSON to start
- Outputs: an in-memory hypergraph object; helpers to add/query hyperedges and list an entity's incident hyperedges
- Dependencies: HyperNetX (pip); Python 3.x
- Assumptions: knowledge fits in memory (small toy set, few dozen hyperedges); each fact is representable as one hyperedge over ≥2 entities
- Validation: round-trip test — insert known facts, retrieve them, confirm entity↔hyperedge membership; assert hyperedge count and arity match the input
- Limitations: no persistence (rebuilt each run); no dedup/versioning; toy scale only; no retrieval logic yet (that's a later block)
- Review status: Draft
- Audit note: