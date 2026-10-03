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
- Hugging Face embeddings
- FAISS vector database
- Semantic similarity search
- Retrieval relevance threshold
- Retrieval-Augmented Generation
- Agent-based workflow
- Planner agent
- Retriever agent
- Reasoning agent
- Validator agent
- Source-grounded answers
- Safe abstention when evidence is insufficient
- Prompt-injection guardrails
- Secret/API-key protection
- Empty-input validation
- Hallucination evaluation
- Answer-quality evaluation
- ROUGE-L evaluation
- BLEU evaluation
- Retrieved-evidence display
- Streamlit user interface

## Technology Stack

- Python
- Streamlit
- LangChain
- LangGraph
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
FAISS Vector Store
        ↓
User Question
        ↓
Safety Guardrail
        ↓
Planner Agent
        ↓
Retriever Agent
        ↓
Relevance Threshold Check
        ↓
Reasoning Agent
        ↓
Validator Agent
        ↓
Grounded Answer
        ↓
Evaluation Metrics