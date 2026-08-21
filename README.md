# Diagnostics_model

Takes medical data and builds a hypergraph (entities as nodes, n-ary facts as
role-typed hyperedges), then saves it.

Embeds the hypergraph two ways for comparison: a real-valued baseline
(TransE-style) and a **complex arm** (RotatE-style), where each concept gets a
magnitude and a phase. These embeddings give the *static* relationships between
tokens — a fixed angle per pair.

We then prompt the machine. Over evolution time *t*, we watch the concepts undergo
**unitary (norm-preserving) evolution** in Hilbert space, and measure how the
*relative angle between token pairs* drifts from its starting value —
Δ_jk(t) = θ_jk(t) − θ_jk(0). This drift, visible only because the system is complex
and unitary, is the observable.

## Introduction
This project visualises concept drift in a HyperRAG system operating over simple medical datasets. 
As the system answers a query using a HyperRAG network, a sparse autoencoder identifies the concepts it relies on, and complex (quantum-inspired) 
linear algebra gives each concept a magnitude and an angle in Hilbert space; magnitude for how strongly the concept is present, 
angle for its relation to other concepts. Plotting these across queries turns the similarities and differences 
between concepts into visible geometry: as the query changes, the relative angles between concepts open and close, and that movement is the drift. 
The aim is to make the system's shifting internal concepts legible in a way a real-valued, magnitude-only view cannot.
We want to see how the system judges relations in a Hilbert space, and how those relations change over different prompts.
We also investigate whether representing concepts with complex-valued (quantum-inspired) linear algebra can reveal information about polysemy and 
concept relationships that a real-valued vector space cannot.

## Visualisation 
The below image describes the angular relationship between concepts at different time t's.
Magnitude (length of each hand) and frequency are fixed. This is for V2 where we cna relate each concept to another with a relationship matrix. Currently they are all diagonalised in Hilbert space. 

![Relationship between concepts over time. Fixed magnitude and frequency, V1][V1_visualisation.png]