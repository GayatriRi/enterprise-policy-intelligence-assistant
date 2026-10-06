def retrieve_documents(vector_store, query, k=3):
    """
    Retrieve the most relevant document chunks
    for a user's natural-language query.
    """

    results_with_scores = vector_store.similarity_search_with_relevance_scores(
        query,
        k=k,
    )

    results = []

    for document, score in results_with_scores:
        print("RETRIEVAL SCORE:", score)

        if score >= 0.30:
            results.append(document)

    return results