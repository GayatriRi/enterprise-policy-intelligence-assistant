import hashlib

import streamlit as st

from src.ingestion.loaders import load_document
from src.ingestion.chunker import split_documents
from src.retrieval.vector_store import build_vector_store
from src.retrieval.retriever import retrieve_documents
from src.generation.rag import generate_answer
from src.agents.workflow import run_agent_workflow
from src.safety.guardrails import validate_query

st.set_page_config(
    page_title="Enterprise Policy Intelligence Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Enterprise Policy Intelligence Assistant")

st.write(
    "A Generative AI and Agentic RAG assistant for querying enterprise documents "
    "with grounded answers, safety guardrails, and evaluation metrics."
)

st.info(
    "How to use: Upload one or more supported documents, then ask a question "
    "about their contents."
)

st.divider()

st.subheader("Upload Enterprise Documents")

uploaded_files = st.file_uploader(
    "Upload PDF, TXT, CSV, or Excel files",
    type=["pdf", "txt", "csv", "xlsx", "xls"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) selected successfully.")

if "processed_files" not in st.session_state:
    st.session_state["processed_files"] = {}

processed_files = st.session_state["processed_files"]
active_files = {}
for uploaded_file in uploaded_files:
    content_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    file_identity = (uploaded_file.name, content_hash)
    active_files.setdefault(file_identity, uploaded_file)

for file_identity in list(processed_files):
    if file_identity not in active_files:
        del processed_files[file_identity]

for file_identity, uploaded_file in active_files.items():
    if file_identity not in processed_files:
        entry = {
            "file_identity": file_identity,
            "content_hash": file_identity[1],
            "document_count": 0,
            "chunks": [],
            "vector_store": None,
            "last_submitted_question": None,
            "workflow_result": None,
            "processing_error": None,
            "submission_error": None,
        }
        try:
            documents = load_document(uploaded_file)
            entry["document_count"] = len(documents)
            entry["chunks"] = split_documents(documents)
            entry["vector_store"] = build_vector_store(entry["chunks"])
        except Exception as error:
            entry["processing_error"] = str(error)
        processed_files[file_identity] = entry

    entry = processed_files[file_identity]
    if entry["processing_error"] is not None:
        st.error(f"Could not process {uploaded_file.name}: {entry['processing_error']}")
        continue

    st.write(f"✅ **{uploaded_file.name}**")
    chunks = entry["chunks"]
    st.write(f"Loaded {entry['document_count']} document section(s).")
    st.write(f"Created {len(chunks)} text chunk(s).")
    st.success("FAISS vector store created successfully.")

    with st.expander(f"Preview: {uploaded_file.name}"):
        if chunks:
            preview = chunks[0].page_content[:1000]
            st.text(preview)

    st.divider()
    st.subheader("Ask a Question")

    widget_identity = hashlib.sha256(
        (file_identity[0] + "\0" + file_identity[1]).encode("utf-8")
    ).hexdigest()
    with st.form(key=f"question_form_{widget_identity}"):
        query = st.text_input(
            "Enter a question about the uploaded document:",
            key=f"query_{widget_identity}",
        )
        submitted = st.form_submit_button("Ask")

    if submitted:
        entry["submission_error"] = None
        try:
            guardrail_result = validate_query(query)
            if not guardrail_result["allowed"]:
                entry["submission_error"] = guardrail_result["message"]
            else:
                workflow_result = run_agent_workflow(entry["vector_store"], query)
                entry["last_submitted_question"] = query
                entry["workflow_result"] = workflow_result
        except Exception as error:
            entry["submission_error"] = f"Could not answer question: {error}"

    if entry["submission_error"] is not None:
        st.error(entry["submission_error"])

    workflow_result = entry["workflow_result"]
    if workflow_result is not None:
        st.caption(f"Showing result for: {entry['last_submitted_question']}")
        answer = workflow_result["answer"]
        documents = workflow_result["documents"]
        validation = workflow_result["validation"]
        plan = workflow_result["plan"]
        retrieval_evaluation = workflow_result["retrieval_evaluation"]
        answer_evaluation = workflow_result["answer_evaluation"]
        hallucination_evaluation = workflow_result["hallucination_evaluation"]
        answer_quality_evaluation = workflow_result["answer_quality_evaluation"]
        rouge_evaluation = workflow_result["rouge_evaluation"]
        bleu_evaluation = workflow_result["bleu_evaluation"]

        st.write("### Agent Plan")

        for step in plan["steps"]:
            st.write(f"- {step}")

        st.write("### AI Answer")
        st.write(answer)

        st.write("### Validation")

        if validation["is_valid"]:
            st.success(validation["message"])
        else:
            st.error(validation["message"])

        st.write("### Evaluation")

        st.write(
            f"Retrieval status/count: {retrieval_evaluation['message']}"
        )

        st.write(
            f"Answer: {answer_evaluation['message']}"
        )

        st.write(
            f"Evidence support: {hallucination_evaluation['message']}"
        )

        st.write(
            f"Binary support-check result: {answer_quality_evaluation['message']}"
        )

        st.write(
            rouge_evaluation["message"]
        )

        st.write(
            bleu_evaluation["message"]
        )

        st.write("### Retrieved Evidence")

        for index, result in enumerate(documents, start=1):
            with st.expander(f"Result {index}"):
                st.write(result.page_content)

if not uploaded_files:
    st.info(
        "Upload one or more enterprise documents to begin."
    )