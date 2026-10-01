from rouge_score import rouge_scorer
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
def evaluate_answer_quality(answer, documents):
    """
    Basic answer-quality score based on grounding.
    Returns a score from 0 to 100.
    """

    if not answer or not documents:
        return {
            "score": 0,
            "message": "Answer quality could not be evaluated.",
        }

    context = " ".join(
        document.page_content.lower()
        for document in documents
    )

    answer_words = [
        word.strip(".,!?")
        for word in answer.lower().split()
        if len(word.strip(".,!?")) > 4
    ]

    if not answer_words:
        return {
            "score": 0,
            "message": "Answer did not contain enough meaningful content.",
        }

    supported_words = [
        word
        for word in answer_words
        if word in context
    ]

    grounding_ratio = len(supported_words) / len(answer_words)

    score = round(grounding_ratio * 100)

    return {
        "score": score,
        "message": f"Answer quality score: {score}/100",
    }
def evaluate_rouge(answer, documents):
    """
    Calculate ROUGE-L between the generated answer
    and the retrieved document content.
    """

    if not answer or not documents:
        return {
            "rouge_l": 0.0,
            "message": "ROUGE score could not be calculated.",
        }

    reference_text = " ".join(
        document.page_content
        for document in documents
    )

    scorer = rouge_scorer.RougeScorer(
        ["rougeL"],
        use_stemmer=True,
    )

    scores = scorer.score(
        reference_text,
        answer,
    )

    rouge_l = round(scores["rougeL"].fmeasure, 3)

    return {
        "rouge_l": rouge_l,
        "message": f"ROUGE-L score: {rouge_l}",
    }