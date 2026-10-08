import re
import unicodedata


_INVISIBLE_CHARACTERS = str.maketrans(
    "", "", "\u200b\u200c\u200d\u2060\ufeff\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
)
_DISCUSSION = re.compile(
    r"^(?:please\s+)?(?:explain|describe|summari[sz]e|analy[sz]e|discuss|review|what|how|why)\b"
)
_QUOTED_TEXT = re.compile(r"(?<!\w)(?:\"[^\"]{1,500}\"|'[^']{1,500}')(?!\w)")
_REPORTING_CONTEXT = re.compile(
    r"\b(?:says|states|reads|contains|example|phrase|text|wording|message)\s*[:=]?\s*$"
)
_GAP = r"(?:[\s,:-]+[\w'-]+){0,6}?[\s,:-]+"
_DISCLOSURE = r"\b(?:reveal|show|print|output|display|disclose|expose|repeat|dump)\b"
_PROHIBITION = re.compile(
    r"\b(?:never|(?:must|should|shall|may|can|will|do|does)\s+not|"
    r"don't|doesn't|cannot|can't|(?:is|are)\s+not\s+(?:allowed|permitted)\s+to)"
    r"\s+(?:ever\s+)?$"
)
_PATTERNS = [
    ("instruction override", re.compile(
        r"\b(?:ignore|disregard|forget|override|bypass|replace|discard|set\s+aside)\b" + _GAP
        + r"(?:instructions?|rules?|guidance|directions?|user\s+(?:question|request)|system\s+prompt|"
        r"safety\s+(?:checks|guardrails?)|everything\s+you\s+(?:were|have\s+been)\s+told)\b"
    )),
    ("role impersonation", re.compile(
        r"\b(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|switch\s+to|enter)\b"
        + _GAP + r"(?:system|admin(?:istrator)?|developer)\b"
    )),
    ("role override marker", re.compile(
        r"\b(?:system|developer|admin(?:istrator)?)\s+(?:override|message|instructions?)\s*:"
        r"|<\s*/?\s*(?:system|developer|assistant)\s*>|\[\s*(?:system|developer)\s*\]"
    )),
    ("hidden prompt extraction", re.compile(
        _DISCLOSURE + _GAP
        + r"(?:system|developer|hidden|internal)\s+(?:prompts?|instructions?|messages?)\b"
    )),
    ("credential disclosure", re.compile(
        _DISCLOSURE + _GAP
        + r"(?:api[\s_-]*keys?|secret[\s_-]+keys?|secrets?(?!\s+keys?\b)|"
        r"credentials?|passwords?|access[\s_-]+tokens?)\b"
        r"(?![\s_-]+(?:policy|policies|rotation|management|requirements|guidelines|procedures?)\b)"
    )),
    ("environment disclosure", re.compile(
        r"\b(?:reveal|show|print|output|display|disclose|expose|dump|read|open|cat)\b"
        + _GAP + r"(?:environment\s+variables?|\.env)\b"
    )),
    ("execution of embedded instructions", re.compile(
        r"\b(?:follow|obey|execute)\b" + _GAP
        + r"(?:quoted|embedded|above|following|document)\s+instructions?\b"
    )),
]


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.translate(_INVISIBLE_CHARACTERS)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(text.split())


def _detect_injection(text, allow_quoted_discussion=False):
    normalized = _normalize(text)
    quoted_mentions = []
    if allow_quoted_discussion and _DISCUSSION.match(normalized):
        for quoted in _QUOTED_TEXT.finditer(normalized):
            prefix = normalized[max(0, quoted.start() - 160):quoted.start()]
            if _REPORTING_CONTEXT.search(prefix):
                quoted_mentions.append(quoted.span())

    for category, pattern in _PATTERNS:
        for match in pattern.finditer(normalized):
            # A local prohibition is policy language, not a disclosure request.
            # Do not exempt other categories or later positive commands.
            if category == "credential disclosure" and _PROHIBITION.search(normalized[:match.start()]):
                continue
            if any(start < match.start() and match.end() < end for start, end in quoted_mentions):
                continue
            return category
    return None


def validate_query(query):
    """
    Screen queries for deterministic injection patterns, not a safety guarantee.
    """

    if not query or not _normalize(query):
        return {
            "allowed": False,
            "message": "Please enter a valid question.",
        }

    category = _detect_injection(query, allow_quoted_discussion=True)
    if category:
        return {
            "allowed": False,
            "message": f"This request is blocked by the safety guardrail: suspected {category}.",
        }

    return {
        "allowed": True,
        "message": "Query passed deterministic screening; safety is not guaranteed.",
    }


def validate_retrieved_content(documents):
    """Screen each complete retrieved chunk without removing or rewriting it."""
    for index, document in enumerate(documents or [], start=1):
        category = _detect_injection(document.page_content or "")
        if category:
            return {
                "allowed": False,
                "message": f"Retrieved evidence chunk {index} was blocked: suspected {category}.",
            }
    return {
        "allowed": True,
        "message": "Retrieved evidence passed deterministic screening; safety is not guaranteed.",
    }