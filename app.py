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
    "A Generative AI and Agentic RAG application for querying enterprise documents."
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

    for uploaded_file in uploaded_files:
        try:
            documents = load_document(uploaded_file)
            chunks = split_documents(documents)
            vector_store = build_vector_store(chunks)

            st.write(f"✅ **{uploaded_file.name}**")
            st.write(f"Loaded {len(documents)} document section(s).")
            st.write(f"Created {len(chunks)} text chunk(s).")
            st.success("FAISS vector store created successfully.")

            with st.expander(f"Preview: {uploaded_file.name}"):
                if chunks:
                    preview = chunks[0].page_content[:1000]
                    st.text(preview)

            st.divider()

            st.subheader("Ask a Question")

            query = st.text_input(
                "Enter a question about the uploaded document:",
                key=f"query_{uploaded_file.name}",
            )

            if query:
                guardrail_result = validate_query(query)

                if not guardrail_result["allowed"]:
                    st.error(guardrail_result["message"])

                else:
                    workflow_result = run_agent_workflow(
                        vector_store,
                        query,
                    )

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
                         f"Retrieval: {retrieval_evaluation['message']}"
                    )

                    st.write(
                         f"Answer: {answer_evaluation['message']}"
         )    
                    st.write(
                         f"Hallucination Check: {hallucination_evaluation['message']}"
    )
                    st.write(
                         f"Answer Quality: {answer_quality_evaluation['message']}"
         )
                    st.write(
                         f"ROUGE: {rouge_evaluation['message']}"
   )
                    st.write(
                         f"BLEU: {bleu_evaluation['message']}"
  )
                    st.write("### Retrieved Evidence")

                    for index, result in enumerate(documents, start=1):
                        with st.expander(f"Result {index}"):
                            st.write(result.page_content)

        except Exception as error:
            st.error(
                f"Could not process {uploaded_file.name}: {error}"
            )

else:
    st.info(
        "Upload one or more enterprise documents to begin."
    )