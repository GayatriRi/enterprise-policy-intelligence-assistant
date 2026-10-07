from langchain_community.vectorstores import FAISS

from src.retrieval.embeddings import get_embeddings


def build_vector_store(chunks):
    """
    Build an in-memory FAISS vector store from document chunks.
    """

    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    return vector_store