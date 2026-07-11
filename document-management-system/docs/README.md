# AI Document Pipeline

A multi-tenant document ingestion pipeline that classifies, extracts, and routes business documents using Gemini Flash. Built as a project to demonstrate AI product thinking — every design decision is backed by measured experiments.

## What it does

Upload a document (invoice, purchase order, complaint, or contract). The pipeline:
1. Classifies the document type using Gemini Flash
2. Extracts structured fields using a 4-layer prompt and JSON schema
3. Routes to auto-approve (high confidence) or human review queue (low confidence)
4. Logs every run with cost, latency, and field-level detail

For long documents (contracts, policies), a RAG pipeline chunks the document by section, embeds each chunk, and retrieves the most relevant context per field before extraction.

## Stack

- **Gemini Flash** — classification and extraction (single combined call)
- **gemini-embedding-001** — chunk embeddings for RAG
- **Streamlit** — demo UI with document upload, triage queue, observability, and config
- **SQLite** — run logging and staging queue
- **Python** — no framework, raw `requests` calls to Gemini API

## Project structure

```
demo-app.py                  # Streamlit app — the demo
experiments.py               # 7 experiments comparing design choices
evals.py                     # Eval runner — promotes winning config to live
document-generator.py        # Generates test documents + ground truth
test_samples/                # 4 test documents + ground_truth.json
evals/
  winners.json               # Winning config (filled in after reviewing experiments)
  results/
    detail_20260710_064946.txt   # Full experiment results — field breakdown + RAG detail
.streamlit/
  config.toml                # Theme config
config/
  pyproject.toml             # Dependencies
  uv.lock                    # Lock file
```

## Running the demo

```bash
# Install dependencies
pip install streamlit requests pypdf

# Run the app
cd C:/ai-experiments/document-management-system
streamlit run demo-app.py
```

Paste your Gemini API key in the sidebar. Upload any of the test documents from `test_samples/`.

## Running experiments

```bash
python experiments.py --api-key YOUR_GEMINI_KEY
```

Runs all 7 experiments and writes results to `evals/results/`. Review the detail file, fill in `evals/winners.json`, then promote:

```bash
python evals.py --api-key YOUR_GEMINI_KEY --promote
```

## The 7 experiments

| # | Experiment | Winner | Why |
|---|---|---|---|
| 1 | Model | Gemini Flash | Same precision, 25–130× cheaper than GPT-4o |
| 2 | Call architecture | One combined call | 4× cheaper on long docs, same quality |
| 3 | Prompt quality | Full 4-layer prompt | Minimal prompt missed key semantic detail in complaint |
| 4 | Retrieval strategy | Field-targeted | Contract ID page 1, Governing Law page 28 — one query misses both |
| 5 | Chunking | Section-aware | Governing Law is 4 lines — word-window buried it in noise |
| 6 | Retrieval K | K=3 | K=1 fails when top chunk is wrong, K=5 adds noise |
| 7 | Query formulation | Specific query | Generic sim=0.57, specific sim=0.77 — right chunk retrieved |

## The 4-layer prompt

| Layer | Written by | Content |
|---|---|---|
| 1 | Operator (us) | Role, exact-values constraint, null rule, jailbreak guard |
| 2 | Tenant | Document type description — what makes this type distinctive |
| 3 | Operator | Per-field guide — where to find each field, expected format |
| 4 | Pipeline | JSON schema — forces structured output, null for missing |

Layer 1 includes a jailbreak guard: if the document contains instructions to ignore these rules, the model ignores them and extracts fields normally.

## Key design decisions

**No fast-track.** Every document goes through GenAI. This keeps the system simpler and ensures every result has a confidence score.

**Section-aware chunking.** Detects numbered clauses (`17. GOVERNING LAW`), schedules, and exhibits. Each section becomes its own chunk with a focused embedding. Falls back to word-window if no structure is found.

**Field-targeted RAG.** One embedding query per field using the full field description as the query. Each field retrieves its own top-3 chunks. The extraction prompt shows the model which sections correspond to which field.

**Eval gate.** No config change goes live without running against the golden dataset. Overall precision ≥ 85%, no doc type below 75%. Fails any condition → stays pending.