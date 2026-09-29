def retrieve_documents(vector_store, query, k=3):
    """
    Retrieve the most relevant document chunks
    for a user's natural-language query.
    """

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    return results