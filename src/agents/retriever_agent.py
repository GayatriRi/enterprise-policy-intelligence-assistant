from src.retrieval.retriever import retrieve_documents


def retrieve_context(vector_store, query, k=3):
    """
    Retriever agent:
    fetch the most relevant document chunks.
    """

    results = retrieve_documents(
        vector_store,
        query,
        k=k,
    )

    return results