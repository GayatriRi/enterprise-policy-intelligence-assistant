# Enterprise Policy Intelligence Assistant

A Generative AI and Agentic RAG application that allows users to upload enterprise documents and ask natural-language questions.

## Project Overview

The goal of this project is to build an AI agent-based knowledge and decision support system for enterprise documents.

Users will be able to upload documents in multiple formats, including:

- PDF
- TXT
- CSV
- Excel

The application will process the documents, split them into chunks, generate embeddings, store them in a vector database, retrieve relevant information, and generate grounded answers using a Large Language Model.

## Planned Features

- Multi-format document upload
- PDF, TXT, CSV, and Excel ingestion
- Text chunking
- HuggingFace embeddings
- FAISS vector database
- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Agent-based planning and routing
- Intelligent retrieval
- Evidence grading
- Query rewriting when needed
- LLM-based response generation
- Final answer validation
- Source-grounded answers
- Streamlit user interface
- Error handling and input validation

## Planned Technology Stack

- Python
- Streamlit
- LangChain
- LangGraph
- Groq
- HuggingFace
- Sentence Transformers
- FAISS
- Pandas
- PyPDF

## Planned Agent Workflow

```text
User Question
     ↓
Planner / Router
     ↓
Retriever
     ↓
Evidence Grader
     ↓
Evidence sufficient?
   Yes / No
    ↓     ↓
Generate  Rewrite Query
    ↑        ↓
    └── Retrieve Again
          ↓
Validator
          ↓
Final Grounded Answer
+ Source Citations
Project Status

Project foundation and environment setup are currently in progress.

Security

API keys and other secrets will be stored locally in a .env file and will not be committed to GitHub.

Future Documentation

This README will be updated during development with:

Installation instructions
System architecture
Agent roles
Application workflow
Deployment steps
Testing instructions
Limitations
Challenges faced
Future improvements