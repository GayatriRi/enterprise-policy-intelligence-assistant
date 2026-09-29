from src.agents.planner import create_plan
from src.agents.retriever_agent import retrieve_context
from src.agents.reasoner_agent import reason_over_context
from src.agents.validator_agent import validate_answer


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

    return {
        "plan": plan,
        "documents": documents,
        "answer": answer,
        "validation": validation,
    }