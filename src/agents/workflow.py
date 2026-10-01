from src.agents.planner import create_plan
from src.agents.retriever_agent import retrieve_context
from src.agents.reasoner_agent import reason_over_context
from src.agents.validator_agent import validate_answer
from src.evaluation.metrics import (
    evaluate_retrieval,
    evaluate_answer,
    evaluate_hallucination,
    evaluate_answer_quality,
)

def run_agent_workflow(vector_store, query):
    """
    Run the full agentic workflow:
    Planner -> Retriever -> Reasoner -> Validator
    """

    plan = create_plan(query)

    documents = retrieve_context(
        vector_store,
        query,
        k=3,
    )

    answer = reason_over_context(
        query,
        documents,
    )

    validation = validate_answer(
        answer,
        documents,
    )
    retrieval_evaluation = evaluate_retrieval(documents)
    answer_evaluation = evaluate_answer(answer)
    hallucination_evaluation = evaluate_hallucination(
    answer,
    documents,
) 
    answer_quality_evaluation = evaluate_answer_quality(
    answer,
    documents,
)
    return {
        "plan": plan,
        "documents": documents,
        "answer": answer,
        "validation": validation,
        "retrieval_evaluation": retrieval_evaluation,
        "answer_evaluation": answer_evaluation,
        "hallucination_evaluation": hallucination_evaluation,
        "answer_quality_evaluation": answer_quality_evaluation,
    }