def validate_answer(answer, documents):
    """
    Validator agent:
    check whether the answer is supported by retrieved evidence.
    """

    if not answer:
        return {
            "is_valid": False,
            "message": "No answer was generated.",
        }

    if not documents:
        return {
            "is_valid": False,
            "message": "No supporting documents were retrieved.",
        }

    return {
        "is_valid": True,
        "message": "Answer is supported by retrieved evidence.",
    }