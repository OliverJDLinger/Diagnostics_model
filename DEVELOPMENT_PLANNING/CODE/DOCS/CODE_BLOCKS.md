# CODE BLOCKS: Quantum HyperRAG + sparce autoencoder
Virtual env created name venv-olie
Folder structure (Capitals = folders)


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
- Block name: HyperGraph
- Purpose: store entities as nodes and n-ary facts as hyperedges; the hyperedge is the shared concept unit for later comparison and visualisation
- Phase: 1
- Files: hypergraph/schema.py, store.py, persistence.py, init.py; tests/test_hypergraph_store.py
- Inputs: entity list + n-ary facts (each fact = a set of entities + a relation label), as dict/JSON to start
- Outputs: an in-memory hypergraph object; helpers to add/query hyperedges and list an entity's incident hyperedges
- Dependencies: Python 3.x, This section is just constructing a JSON hypergrpah it does not depend on HyperNetX
- Assumptions: Data is ordered.
- Validation: round-trip test — insert known facts, retrieve them, confirm entity↔hyperedge membership; assert hyperedge count and arity match the input
- Limitations: Limited to a small data set of ordered data
- Review status: In review
- Audit note:

## CODE BLOCK [1]
- Block name: quantum embedding Embedding
- Purpose: Create  embeddings (complex)
- Phase: 2
- Files:
- Inputs: Hyperedge netowrk, stored by persistence.py
- Outputs: Real Word embeddings for our entities, relationships, and roles.
- Dependencies: 
- Assumptions: 
- Validation: 
- Limitations: 
- Review status: 
- Audit note:

## CODE BLOCK [2]
- Block name: Real embedding Embedding
- Purpose: Create embeddings (non-complex)
- Phase: 2
- Files:
- Inputs: 
- Outputs:
- Dependencies: 
- Assumptions: 
- Validation: 
- Limitations: 
- Review status: 
- Audit note: