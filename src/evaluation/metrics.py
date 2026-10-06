import re

from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

from src.agents.validator_agent import validate_answer


def is_abstention(answer):
    """Recognize standalone abstention wording, without judging its correctness."""

    if not answer:
        return False

    answer_text = " ".join(answer.casefold().split()).strip('"\'').rstrip(".!?")

    abstention_patterns = [
        r"(?:i |we )?(?:could not|cannot|can't) find enough information"
        r"(?: in (?:the )?(?:uploaded )?documents?)?",
        r"(?:there is )?not enough information"
        r"(?: in (?:the )?(?:uploaded )?documents?)?",
        r"(?:the |this )?(?:uploaded )?documents? (?:does|do) not provide "
        r"(?:enough )?information(?: to answer(?: (?:this|the|your) question)?)?",
        r"(?:the )?information is not available"
        r"(?: in (?:the )?(?:uploaded )?documents?)?",
        r"(?:i |we )?cannot determine(?: (?:this|the answer))? "
        r"from (?:the )?uploaded documents?",
    ]

    return any(
        re.fullmatch(pattern, answer_text) is not None
        for pattern in abstention_patterns
    )


def evaluate_retrieval(documents):
    """
    Basic retrieval evaluation.
    Reports retrieval availability and count, without assessing relevance.
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
        "message": f"{len(documents)} document chunk(s) retrieved; relevance not assessed.",
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
def _evaluate_support(answer, documents):
    """Share assessment status between the legacy evaluation interfaces."""
    if is_abstention(answer):
        return None, "Abstention detected; correctness not assessed"

    if not answer or not answer.strip():
        return None, "Evidence support not assessed: no answer was generated."

    if not any(
        document.page_content and document.page_content.strip()
        for document in (documents or [])
    ):
        return None, "Evidence support not assessed: no usable retrieved evidence."

    validation = validate_answer(answer, documents)
    if validation["is_valid"]:
        return True, (
            "Deterministic evidence-support pass; "
            "factual correctness is not independently verified."
        )
    return False, f"Deterministic evidence-support failure: {validation['message']}"


def evaluate_hallucination(answer, documents):
    """Legacy key: False=heuristic pass, True=failure, None=not assessed."""
    supported, message = _evaluate_support(answer, documents)
    return {
        "hallucination_detected": None if supported is None else not supported,
        "message": message,
    }


def evaluate_answer_quality(answer, documents):
    """Binary support indicator: 100=pass, 0=failure, None=not assessed.

    This is neither an overall quality percentage nor a probability.
    """
    supported, message = _evaluate_support(answer, documents)
    score = None if supported is None else (100 if supported else 0)
    return {
        "score": score,
        "message": message if score is None else f"Binary support indicator: {score}. {message}",
    }


def evaluate_rouge(answer, documents):
    """
    Calculate ROUGE-L between the generated answer
    and the retrieved document content, not factual correctness.
    """

    if is_abstention(answer):
        return {
            "rouge_l": None,
            "message": "ROUGE-L against retrieved context not assessed for abstention.",
        }

    reference_text = " ".join(
        document.page_content
        for document in (documents or [])
        if document.page_content and document.page_content.strip()
    )

    if not answer or not answer.strip() or not reference_text.strip():
        return {
            "rouge_l": None,
            "message": "ROUGE-L against retrieved context not assessed: missing answer or evidence.",
        }

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
        "message": f"ROUGE-L against retrieved context: {rouge_l} (lexical overlap only).",
     }
def evaluate_bleu(answer, documents):
    """
    Calculate BLEU score between the generated answer
    and the retrieved document content, not factual correctness.
    """

    if is_abstention(answer):
        return {
            "bleu": None,
            "message": "BLEU against retrieved context not assessed for abstention.",
        }

    reference_text = " ".join(
        document.page_content
        for document in (documents or [])
        if document.page_content and document.page_content.strip()
    )

    if not answer or not answer.strip() or not reference_text.strip():
        return {
            "bleu": None,
            "message": "BLEU against retrieved context not assessed: missing answer or evidence.",
        }

    reference_tokens = reference_text.lower().split()
    answer_tokens = answer.lower().split()

    smoothing = SmoothingFunction().method1

    bleu_score = sentence_bleu(
        [reference_tokens],
        answer_tokens,
        smoothing_function=smoothing,
    )

    bleu_score = round(bleu_score, 3)

    return {
        "bleu": bleu_score,
        "message": f"BLEU against retrieved context: {bleu_score} (lexical overlap only).",
    }
