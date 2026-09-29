def validate_query(query):
    """
    Basic guardrail for user queries.
    Blocks empty or obviously unsafe requests.
    """

    if not query or not query.strip():
        return {
            "allowed": False,
            "message": "Please enter a valid question.",
        }

    blocked_terms = [
        "ignore previous instructions",
        "reveal api key",
        "show secret key",
        "print environment variables",
        "show .env",
    ]

    normalized_query = query.lower()

    for term in blocked_terms:
        if term in normalized_query:
            return {
                "allowed": False,
                "message": "This request is blocked by the safety guardrail.",
            }

    return {
        "allowed": True,
        "message": "Query passed safety checks.",
    }