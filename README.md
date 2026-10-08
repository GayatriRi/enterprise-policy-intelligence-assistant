# Enterprise Policy Intelligence Assistant

A Generative AI and Agentic RAG application for querying enterprise documents using natural-language questions.

## Project Overview

The Enterprise Policy Intelligence Assistant is an AI-powered knowledge and decision-support system that allows users to upload enterprise documents and ask questions about their content.

The application uses:

- Retrieval-Augmented Generation (RAG)
- Large Language Models (LLMs)
- Agent-based reasoning
- Semantic retrieval
- Vector search
- Safety guardrails
- Answer validation
- Evaluation metrics

The goal is to generate grounded, context-aware answers based only on retrieved document evidence.

## Supported File Types

The application supports:

- PDF
- TXT
- CSV
- Excel `.xlsx`
- Excel `.xls`

## Core Features

- Multi-format enterprise document upload
- Document loading and parsing
- Text chunking
- Local Hugging Face sentence-transformer embeddings
- In-memory, per-file, session-local FAISS indexes
- Semantic similarity search
- Retrieval relevance threshold
- Retrieval-Augmented Generation
- Deterministic agent-style workflow
- Planner agent
- Retriever agent
- Reasoning agent
- Validator agent
- Evidence-constrained answer generation
- Prompted abstention when evidence is insufficient
- Prompt-injection guardrails
- Credential/environment-disclosure request screening
- Empty-input validation
- Deterministic evidence-support evaluation
- Binary support-check indicator
- ROUGE-L and BLEU diagnostics against retrieved context
- Retrieved-evidence display
- Streamlit user interface
- Explicit Ask forms and session reuse of indexes and submitted results

## Technology Stack

- Python
- Streamlit
- LangChain
- Groq
- Hugging Face
- Sentence Transformers
- FAISS
- Pandas
- PyPDF
- OpenPyXL
- xlrd
- python-dotenv
- NLTK
- rouge-score

## Architecture and Components

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit uploads, per-file Ask forms, session state, errors, saved results, and evidence display. |
| `src/ingestion` | Load supported formats, preserve source metadata, and split documents into overlapping text chunks. |
| `src/retrieval` | Run local embeddings, build in-memory FAISS indexes, and retrieve chunks using a relevance threshold. |
| `src/agents` | Run the fixed planner → retriever → reasoner → validator pipeline and collect evaluations. |
| `src/generation` | Screen generation inputs and invoke Groq with structured system/human messages. |
| `src/safety` | Deterministically screen user queries and retrieved evidence for suspicious instructions. |
| `src/evaluation` | Report availability, heuristic evidence support, and lexical diagnostics. |

The planner returns fixed steps; this is a deterministic agent-style pipeline without autonomous replanning. Embeddings use `sentence-transformers/all-MiniLM-L6-v2` locally. Each uploaded file has its own in-memory FAISS object in Streamlit session state; the application does not save or load persisted indexes.

## Application Workflow

```text
User uploads document
        ↓
Document Loader
        ↓
Text Chunking
        ↓
Embedding Generation
        ↓
Session-local FAISS Index
        ↓
User Question + Ask Submission
        ↓
Safety Guardrail
        ↓
Planner Agent
        ↓
Retriever Agent
        ↓
Relevance Threshold Check
        ↓
Generation-boundary Query and Evidence Screening
        ↓
Reasoning Agent / Groq Generation
        ↓
Validator Agent
        ↓
Evaluation Metrics
        ↓
Answer, Validation Status, and Retrieved Evidence Display
```

## Setup and Configuration (Windows)

Python **3.13.14** is currently tested locally. Compatibility with other Python versions has not been verified.

On a fresh checkout, open PowerShell in the project root and run:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally and replace the placeholder with your own Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

The real `.env` must never be committed or included in the submission. `.env.example` is the shareable template. Groq is the implemented generation provider; Gemini is not integrated.

Launch the application from the project root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

These commands use the virtual-environment interpreter directly, so activation is optional.

## Example Usage

1. Upload an included sample such as `travel_policy.pdf` or `sample_policy.txt`.
2. Enter a question in that file's form and select **Ask**.
3. Review the answer, validation status, evaluation messages, and retrieved evidence.

| Upload | Representative question | Expected factual content or behavior |
|---|---|---|
| `travel_policy.pdf` | What is the maximum daily meal allowance during approved business travel? | Employees may claim up to **$75 per day for meals** during approved business travel. |
| `sample_policy.txt` | How many days of paid annual leave do employees receive? | **15 days of paid annual leave per year**. |
| `travel_policy.pdf` | How many days of annual leave do employees receive? | No supporting evidence should be retrieved; an insufficient-information abstention is expected. |

Generated wording can vary, and validation may reject some otherwise reasonable paraphrases. Multiple uploads have separate questions and indexes. Editing a question does not submit it; ordinary reruns reuse processed files and saved results. Selecting Ask again intentionally runs the workflow again.

## Safety and Guardrails

User queries and retrieved evidence receive deterministic screening. Generation rechecks the query and screens the evidence before invoking Groq; flagged inputs stop before the LLM call. Suspicious chunks are not silently removed.

Generation uses separate system and human messages. The fixed system instructions treat the question and retrieved document text as untrusted data; the human message contains JSON-serialized fields. The system prompt instructs the model not to follow instructions embedded in the evidence.

These controls are defensive heuristics, not a guarantee against every prompt-injection attack. API keys configure the client and are not inserted into the generation messages.

## Evaluation Metrics

| Result | Meaning |
|---|---|
| Retrieval status/count | Retrieved chunk availability and count; not a relevance assessment. |
| Answer presence | Whether a nonempty answer was generated; not correctness. |
| Evidence support | Deterministic validator checks against retrieved evidence; not independent factual verification. |
| Binary support indicator | **100**: support checks pass; **0**: checks fail; **None**: not assessed. This is not a probability or overall quality percentage. |
| ROUGE-L | Lexical sequence overlap against retrieved context, not a factual-ground-truth score. |
| BLEU | Lexical n-gram overlap against retrieved context, not a factual-ground-truth score. |

Standalone abstention is reported as **"Abstention detected; correctness not assessed"** and does not receive an automatic 100. There is no gold/reference-answer comparison in the current evaluation.

## Known Limitations

- Deterministic validation cannot establish complete semantic correctness; some paraphrases fail and some unsupported meanings may escape detection.
- Prompt-injection screening can produce false positives and false negatives.
- Scanned/image-only PDFs are not OCR processed; a document needs extractable text to build an index.
- Questions are answered per uploaded file, without cross-document reasoning.
- Indexes and saved results are session-local; indexes must be rebuilt after a Streamlit session reset.
- Answers that fail validation are still displayed with a warning rather than automatically replaced.
- No-evidence submissions still reach generation; abstention depends on the model following its instructions.

## Reproducibility and Submission

- `requirements.txt` is currently unpinned, so exact dependency reproduction is not guaranteed. Record the installed versions used for your final demonstration.
- First use may download the embedding model from Hugging Face; embeddings run locally after the model is available.
- Groq connectivity and a valid local API key are required for generation. The question and retrieved document text are sent to Groq.
- Commit/share source files, `requirements.txt`, `.env.example`, and sample documents. Never commit or submit the real `.env` or API keys.
- Exclude `.env`, `.venv`, `.git`, `__pycache__`, and stale/generated `vector_store` artifacts from the submission ZIP. `.gitignore` does not automatically exclude them from a manually created ZIP.
- Keep the final submission package under **25 MB**; dependencies and model caches should not be bundled.
