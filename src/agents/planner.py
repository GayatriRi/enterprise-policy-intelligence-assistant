def create_plan(query):
    """
    Create a simple plan for answering the user's question.
    """

    plan = {
        "question": query,
        "steps": [
            "Retrieve relevant document chunks",
            "Reason over the retrieved evidence",
            "Validate the generated answer",
        ],
    }

    return plan