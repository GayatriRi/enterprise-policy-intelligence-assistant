def evaluate_retrieval(documents):
    """
    Basic retrieval evaluation.
    Checks whether relevant documents were retrieved.
    """

    if not documents:
        return {
            "retrieval_success": False,
            "retrieved_count": 0,
            "message": "No documents were retrieved.",
        }

    return {
        "retrieval_success": True,
        "retrieved_count": len(documents),
        "message": f"{len(documents)} relevant document chunk(s) retrieved.",
    }


def evaluate_answer(answer):
    """
    Basic answer evaluation.
    Checks whether an answer was generated.
    """

    if not answer or not answer.strip():
        return {
            "answer_generated": False,
            "message": "No answer was generated.",
        }

    return {
        "answer_generated": True,
        "message": "Answer was generated successfully.",
    }
def evaluate_hallucination(answer, documents):
    """
    Basic hallucination check.
    Verifies whether the generated answer is grounded
    in the retrieved document content.
    """

    if not answer or not documents:
        return {
            "hallucination_detected": True,
            "message": "Unable to verify the answer against retrieved evidence.",
        }

    context = " ".join(
        document.page_content.lower()
        for document in documents
    )

    answer_text = answer.lower()

    important_words = [
        word
        for word in answer_text.split()
        if len(word) > 4
    ]

    supported_words = [
        word
        for word in important_words
        if word.strip(".,!?") in context
    ]

    if important_words and len(supported_words) >= len(important_words) / 2:
        return {
            "hallucination_detected": False,
            "message": "Answer appears grounded in the retrieved evidence.",
        }

    return {
        "hallucination_detected": True,
        "message": "Answer may contain information not supported by the retrieved evidence.",
    }