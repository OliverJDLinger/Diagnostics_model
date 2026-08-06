# HyperRAG Concept-Drift Visualiser — Roadmap

## 1. Scope

**Objective:** Hypergraph RAG + sparse autoencoder to surface hidden concepts, using complex / Hilbert-space embeddings (magnitude + phase). Goal: **visualise concept drift** — a complex embedding gives each concept an angle, so relative angle = interpretable distance between concepts.

**Framing (keep visible):** "Quantum" = the maths (complex amplitudes, phase, unitary/Hermitian) as a representational lens. No quantum hardware, no speedup claim. Guards against the dequantization objection.

**Success (v1):** phase+magnitude view shows drift / interference / alignment that a real-valued, magnitude-only view does not. A null result is still valid and worth recording.

**In scope:**
- Small medical hypergraph (hyperedges = n-ary facts = concept unit).
- Two encoders: real baseline + complex/rotational (RotatE/ComplEx).
- One shared, phase-preserving SAE; concepts anchored to hyperedges.
- Phase+magnitude visualiser (relative phase drift across queries).
- Reproducible experiments + audit trail.

**Out of scope:**
- speedup claims.
- Vision / multimodal arm (deferred — hardest part).
- Causal "which concept drove it" validation (later; v1 is descriptive).
- Clinical / diagnostic use — research prototype only.

---

## 2. Baseline (2026-08-06)
- Repo exists, ready.
- Concept defined (this doc).
- No code, data, encoders, SAE, or visualiser yet.

**Lock first:** (1) smallest useful hypergraph; (2) "hidden concept" = hyperedge / SAE feature; (3) "drift you can see" = magnitude + phase.

---

## 3. Phases

Live tracker. Build order: **hypergraph → SAE → visualiser.**

**Current phase:** Phase 0 — In progress · Next: Phase 1

### Phase 0 — Scope & problem definition
Status: [ ] Not started  [X] In progress  [ ] Complete
- [ ] Define the drift problem in one paragraph
- [ ] Identify target audience
- [ ] Define expected output (visualiser + baseline comparison)
- [ ] Write success criteria (§1)
- [ ] Record assumptions / risks (below)
- [ ] Capture evidence
- [ ] Confirm exit criteria

**Risks (pre-filled):**
- Cross-encoder comparability → anchor to hyperedges; one shared SAE.
- Spurious SAE features → inspect top hyperedges; log artefacts.
- Correlation ≠ causation → no causal claims in v1.
- Medical over-claim → de-identified data; prototype-only.
- Scope creep → vision arm + causal layer out of scope.

### Phase 1 — Hypergraph & schema
Status: [X] Not started  [ ] In progress  [ ] Complete
- [ ] Build small medical hypergraph (hyperedges = n-ary facts)
- [ ] Define schema (entities, hyperedges, attributes)
- [ ] Sample data (few dozen hyperedges + test queries)
- [ ] Confirm hyperedge works as shared concept unit
- [ ] Document toy-data limits
- [ ] Capture evidence
- [ ] Confirm exit criteria

### Phase 2 — Encoders (real + complex)
Status: [X] Not started  [ ] In progress  [ ] Complete
- [ ] Real-valued baseline embedding
- [ ] Complex / rotational embedding (RotatE/ComplEx)
- [ ] Hold all else identical (hypergraph, queries, seeds)
- [ ] Sanity-check retrieval in both arms
- [ ] Note coupling: similarity differs (dot vs Hermitian)
- [ ] Capture evidence
- [ ] Confirm exit criteria

**Exit gate — phase-preservation check** (run on complex arm before the SAE; fail = stop and fix):
- [ ] **Non-degenerate phase (make-or-break, key for visualisation):** phase histogram spread, not collapsed near 0. Collapsed = secretly the real model, nothing to visualise.
- [ ] **Rotation constraint:** relations ≈ unit-modulus (true rotations).
- [ ] **Predictive:** head∘relation ≈ true tail in phase; worse for false triples.
- [ ] **Relational algebra:** inverse ≈ opposite phase; symmetric ≈ 0/π; composition adds phase.
- [ ] **Gauge-stable:** global phase shift leaves *relative* angles unchanged.
- [ ] **Survives plumbing:** phase intact after normalize / store / reduce.

**Storage vs retrieval (don't conflate):**
- **Storage must keep phase (v1):** phase comes from embeddings + SAE, not retrieval. Store complex vectors as interleaved real/imag pairs → thin wrapper on an ordinary store, not a custom RAG.
- **Phase-aware retrieval (later):** Hermitian-inner-product retrieval that exploits interference — defer to Phase 5.

### Phase 3 — Sparse autoencoder
Status: [X] Not started  [ ] In progress  [ ] Complete
- [ ] Train one shared **phase-preserving (complex)** SAE (a real SAE discards the angle)
- [ ] Map features → hyperedges (concept ↔ hyperedge table)
- [ ] Check reconstruction + sparsity
- [ ] Inspect top hyperedges; flag artefacts
- [ ] Document readout (magnitude = present; phase from complex arm)
- [ ] Capture evidence
- [ ] Confirm exit criteria

### Phase 4 — Visualiser (the heart)
Status: [ ] Not started  [ ] In progress  [ ] Complete
- [ ] Precondition: Phase 2 gate passed
- [ ] Concept = vector with magnitude (length) + phase (angle)
- [ ] Render a few concepts under one query (phasor view)
- [ ] Show relative phase between pairs (parallel = reinforce; opposite = interfere)
- [ ] Step across queries → watch drift
- [ ] Side-by-side vs magnitude-only baseline
- [ ] Record one case phase beats baseline (or that it doesn't)
- [ ] Capture evidence
- [ ] Confirm exit criteria

### Phase 5 — Evaluation & iteration
Status: [ ] Not started  [ ] In progress  [ ] Complete
- [ ] Define "phase reveals extra structure" (metric or documented case) Also Add trajectory Hyper RAG
- [ ] Test queries; where phase helps / doesn't
- [ ] Record strengths, weaknesses, failures
- [ ] Go/no-go on scope: phase-aware retrieval / causal layer / vision arm
- [ ] Capture evidence
- [ ] Confirm exit criteria

### Phase 6 — Reproducibility & release
Status: [ ] Not started  [ ] In progress  [ ] Complete
- [ ] Setup instructions + reproducible scripts
- [ ] Examples / usage notes
- [ ] Package to reviewable state
- [ ] Update roadmap + next-iteration plan
- [ ] Capture evidence
- [ ] Confirm exit criteria

---

## 4. Milestone audit
Per milestone: date · phase · objective · inputs/assumptions · changes · evidence · decisions · risks/open questions · next action.

**Checkpoint template:** Date · Phase · Status (Planned / In progress / Complete) · Evidence · Key decision · Next step.

---

## 5. Next actions
1. [ ] Define drift problem in one paragraph (P0)
2. [ ] Build small hypergraph + queries (P1)
3. [ ] Stand up both encoders (P2)
4. [ ] Train minimal shared SAE, name a few concepts (P3)
5. [ ] Prototype phase+magnitude visualiser (P4)
6. [ ] Record first checkpoint

**Smallest validating experiment:** embed the small hypergraph both ways → SAE → plot magnitude+phase for a few hyperedges across a few queries. Phase shows drift the baseline doesn't → premise validated in an afternoon. It doesn't → learned cheaply.

---

## 6. Working rhythm
- Small, testable milestones.
- Record decisions as made; save evidence with code.
- Keep §1 framing visible — no speedup / clinical claims.
- Revisit roadmap when scope changes.