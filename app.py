import streamlit as st

from src.ingestion.loaders import load_document
from src.ingestion.chunker import split_documents
from src.retrieval.vector_store import build_vector_store
from src.retrieval.retriever import retrieve_documents
from src.generation.rag import generate_answer



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
                results = retrieve_documents(
                    vector_store,
                    query,
                    k=3,
                )
                answer = generate_answer(query, results)

                st.write("### AI Answer")
                st.write(answer)

                st.write("### Retrieved Evidence")

                for index, result in enumerate(results, start=1):
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
    
  
