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
_PARAPHRASE_SUPPORT = {
    "get": {"receive", "receives"},
    "can": {"may", "allowed", "allows", "permits"},
    "allowed": {"may", "can", "allows", "permits"},
    "allows": {"may", "can", "allowed", "permits"},
    "permits": {"may", "can", "allowed", "allows"},
    "entitled": {"receive", "receives"},
    "allowance": {"receive", "receives", "entitled"},
}
_OPPOSITE_MODIFIERS = (
    ("paid", "unpaid"), ("required", "optional"),
    ("allowed", "prohibited"), ("permitted", "forbidden"),
)
_DIRECTIONAL_VERBS = {
    "pay": "pay", "pays": "pay", "send": "send", "sends": "send",
    "transfer": "transfer", "transfers": "transfer",
    "assign": "assign", "assigns": "assign",
}
_RELATION_MODALS = {
    "must", "should", "shall", "may", "can", "will", "would", "could", "might",
}
_RELATION_AUXILIARIES = _RELATION_MODALS | {"allowed", "entitled"}


def _normalize(text):
    text = text.casefold().replace("’", "'")
    text = re.sub(r"\bcan't\b", "can not", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"\b(\w+)n't\b", r"\1 not", text)
    # Preserve line boundaries for bullet and claim splitting.
    text = "\n".join(" ".join(line.split()) for line in text.splitlines())
    return re.sub(
        r"^(?:the|this)\s+(?:policy|document|evidence)\s+(?=(?:allows|permits)\b)",
        "",
        text,
    )


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


def _normalize_quantitative_framing(clause, candidate_clause, tokens, candidate):
    """Simplify a bounded monetary framing only after proving it in one clause.

    None means a recognized framing was unsupported. Other constructions,
    including negative ones, retain their original tokens and checks.
    """
    if _negation_scopes(tokens) or _negation_scopes(candidate):
        return tokens

    framing = re.fullmatch(r"(?:the|this)\s+(.+?)\s+is\s+(.+)", clause)
    if not framing:
        return tokens
    head = re.fullmatch(
        r"(?P<maximum>maximum\s+)?(?P<daily>daily\s+)?"
        r"(?P<modifiers>(?:[^\W\d_]+\s+){0,6})"
        r"(?:reimbursement|allowance)(?:\s+(?P<quantity>amount|limit))?",
        framing[1],
    )
    if not head:
        return tokens
    body = _tokens(framing[2])
    if not body or not _NUMBER.fullmatch(body[0]) or body[0][0] not in "$\u20ac\u00a3":
        # Nonmonetary allowances retain the existing generic validation path.
        return tokens

    # Require an explicit monetary entitlement, not just a nearby amount.
    entitlement = re.fullmatch(
        r".+?\s+(?:(?:may|can|are allowed to|are entitled to)\s+(?:claim|receive)"
        r"|(?:are|can be|may be)\s+reimbursed)\s+"
        r"(?:(?P<bound>up to|at most)\s+)?(?P<body>.+)",
        candidate_clause,
    )
    if not entitlement:
        # An identical nominal construction needs no semantic simplification.
        return tokens if clause == candidate_clause else None
    evidence_body = _tokens(entitlement["body"])
    # Preserve every amount, unit, purpose and context token in order. This is
    # deliberately stricter than overlap before removing any framing words.
    if body != evidence_body:
        return None
    if (head["maximum"] or head["quantity"] == "limit") and not entitlement["bound"]:
        return None
    if head["daily"] and not (
        re.search(r"\bper day\b", framing[2])
        and re.search(r"\bper day\b", entitlement["body"])
    ):
        return None

    # Only framing modifiers get this bounded regular-plural comparison.
    # They must all be supported; no unmatched-modifier allowance is used.
    modifiers = []
    for modifier in _tokens(head["modifiers"]):
        equivalent = next(
            (
                word for word in candidate
                if modifier == word
                or (len(modifier) > 3 and modifier + "s" == word)
                or (len(word) > 3 and word + "s" == modifier)
            ),
            None,
        )
        if equivalent is None:
            return None
        modifiers.append(equivalent)
    return modifiers + body


def _lexically_consistent(claim_words, candidate_words):
    """Allow only bounded paraphrases backed by this evidence candidate."""
    unmatched = claim_words - candidate_words
    for first, second in _OPPOSITE_MODIFIERS:
        if (
            (first in unmatched and second in candidate_words)
            or (second in unmatched and first in candidate_words)
        ):
            return False
    return all(
        word in _PARAPHRASE_SUPPORT
        and _PARAPHRASE_SUPPORT[word] & candidate_words
        for word in unmatched
    )


def _directional_signatures(tokens, verbs):
    """Extract local actor/action/object signatures, not global word order."""
    def participant(words):
        return next(
            (
                word for word in words
                if word not in _RELATION_AUXILIARIES
                and word not in _NEGATIONS
                and not _NUMBER.fullmatch(word)
            ),
            None,
        )

    signatures = []
    for index, word in enumerate(tokens):
        if word not in _DIRECTIONAL_VERBS or _DIRECTIONAL_VERBS[word] not in verbs:
            continue
        actor = participant(reversed(tokens[:index]))
        target = participant(tokens[index + 1:])
        signatures.append((actor, _DIRECTIONAL_VERBS[word], target))
    return signatures


def _directional_relationships_match(claim, candidate):
    # A modal immediately before a directional verb identifies a bounded
    # active construction. The corresponding statement may omit the modal.
    verbs = {
        _DIRECTIONAL_VERBS[word]
        for tokens in (claim, candidate)
        for index, word in enumerate(tokens)
        if word in _DIRECTIONAL_VERBS and index > 0
        and tokens[index - 1] in _RELATION_MODALS
    }
    # Without that cue, reject clear reversals without interpreting every
    # noun occurrence (such as "transfer") as an active-voice construction.
    all_verbs = set(_DIRECTIONAL_VERBS.values())
    all_available = _directional_signatures(candidate, all_verbs)
    for actor, verb, target in _directional_signatures(claim, all_verbs):
        if (
            actor is not None and target is not None and actor != target
            and (actor, verb, target) not in all_available
            and (target, verb, actor) in all_available
        ):
            return False
    available = _directional_signatures(candidate, verbs)
    return all(
        signature in available
        for signature in _directional_signatures(claim, verbs)
    )


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
    return (
        _negation_scopes(claim) == _negation_scopes(candidate)
        and _lexically_consistent(claim_words, candidate_words)
        and _directional_relationships_match(claim, candidate)
    )


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
        (clause, tokens)
        for document in (documents or [])
        if document.page_content and document.page_content.strip()
        for clause, tokens in _claims(document.page_content)
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
        supported = False
        for candidate_clause, candidate in evidence_candidates:
            normalized = _normalize_quantitative_framing(
                clause, candidate_clause, tokens, candidate
            )
            if normalized is not None and _supported(normalized, candidate):
                supported = True
                break
        if not supported:
            return {
                "is_valid": False,
                "message": f"Claim could not be verified against retrieved evidence: {clause}",
            }

    return {
        "is_valid": True,
        "message": "All claims pass token-coverage, numeric and negation checks against retrieved evidence.",
    }
