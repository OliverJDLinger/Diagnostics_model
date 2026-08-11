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

