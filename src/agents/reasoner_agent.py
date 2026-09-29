from src.generation.rag import generate_answer


def reason_over_context(query, documents):
    """
    Reasoner agent:
    generate a grounded answer from retrieved evidence.
    """

    answer = generate_answer(
        query,
        documents,
    )

    return answer