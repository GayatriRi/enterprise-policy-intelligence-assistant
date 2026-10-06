import re
from decimal import Decimal


_STOP_WORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "for", "per", "each",
    "is", "are", "was", "were", "be", "been", "being", "do", "does", "did",
    "it", "they", "their", "this", "that", "these", "those",
}
_NEGATIONS = {"not", "no", "never", "without", "neither", "nor"}
_NUMBER = re.compile(r"[$€£]?[+-]?\d+(?:,\d{3})*(?:\.\d+)?%?")
_TOKEN = re.compile(r"[$€£]?[+-]?\d+(?:,\d{3})*(?:\.\d+)?%?|[^\W\d_]+", re.UNICODE)
_CLAUSE_BREAK = re.compile(
    r"(?<!\d)[.!?]|[.!?](?!\d)|[;\n•]|\b(?:and|but|or|however|although|whereas)\b"
)


def _normalize(text):
    text = text.casefold().replace("’", "'")
    text = re.sub(r"\bcan't\b", "can not", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"\b(\w+)n't\b", r"\1 not", text)
    # Preserve line boundaries for bullet and claim splitting.
    return "\n".join(" ".join(line.split()) for line in text.splitlines())


def _tokens(text):
    tokens = []
    for token in _TOKEN.findall(text):
        if _NUMBER.fullmatch(token):
            currency = token[0] if token[0] in "$€£" else ""
            percent = "%" if token.endswith("%") else ""
            value = token.lstrip("$€£").rstrip("%").replace(",", "")
            token = currency + format(Decimal(value).normalize(), "f") + percent
        if token not in _STOP_WORDS:
            tokens.append(token)
    return tokens


def _claims(text):
    return [
        (clause.strip(), _tokens(clause))
        for clause in _CLAUSE_BREAK.split(_normalize(text))
        if _tokens(clause)
    ]


def _negation_scopes(tokens):
    return [
        (token, *tokens[index + 1:index + 4])
        for index, token in enumerate(tokens)
        if token in _NEGATIONS
    ]


def _supported(claim, candidate):
    claim_words, candidate_words = set(claim), set(candidate)
    unmatched = claim_words - candidate_words
    if len(claim_words) < 5:
        if unmatched:
            return False
    elif len(unmatched) > 1 or len(claim_words & candidate_words) / len(claim_words) < 0.8:
        return False

    # Require matching numeric values, currency/percent markers, and a local
    # following token (usually a unit), rather than a number anywhere in a chunk.
    for index, token in enumerate(claim):
        if not _NUMBER.fullmatch(token):
            continue
        following = claim[index + 1:index + 2]
        if not any(
            candidate_token == token
            and (not following or candidate[position + 1:position + 2] == following)
            for position, candidate_token in enumerate(candidate)
        ):
            return False

    # Exact local scopes deliberately reject ambiguous negative paraphrases.
    return _negation_scopes(claim) == _negation_scopes(candidate)


def validate_answer(answer, documents):
    """
    Validator agent:
    conservatively check every claim using token coverage, numbers and negation.
    """

    if not answer or not answer.strip():
        return {
            "is_valid": False,
            "message": "No answer was generated.",
        }

    evidence_candidates = [
        tokens
        for document in (documents or [])
        if document.page_content and document.page_content.strip()
        for _, tokens in _claims(document.page_content)
    ]

    if not evidence_candidates:
        return {
            "is_valid": False,
            "message": "No supporting documents were retrieved.",
        }

    claims = _claims(answer)
    if not claims:
        return {
            "is_valid": False,
            "message": "Answer contains no meaningful claims to validate.",
        }

    for clause, tokens in claims:
        if not any(_supported(tokens, candidate) for candidate in evidence_candidates):
            return {
                "is_valid": False,
                "message": f"Claim could not be verified against retrieved evidence: {clause}",
            }

    return {
        "is_valid": True,
        "message": "All claims pass token-coverage, numeric and negation checks against retrieved evidence.",
    }
