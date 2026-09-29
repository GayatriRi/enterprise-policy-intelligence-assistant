from pathlib import Path

from langchain_community.vectorstores import FAISS

from src.retrieval.embeddings import get_embeddings


FAISS_INDEX_PATH = Path("vector_store/faiss_index")


def build_vector_store(chunks):
    """
    Build a FAISS vector store from document chunks
    and save it locally.
    """

    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    FAISS_INDEX_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        str(FAISS_INDEX_PATH)
    )

    return vector_store


def load_vector_store():
    """
    Load the saved FAISS vector store from disk.
    """

    embeddings = get_embeddings()

    if not FAISS_INDEX_PATH.exists():
        return None

    vector_store = FAISS.load_local(
        str(FAISS_INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store