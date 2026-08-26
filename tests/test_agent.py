from src.agent.agent import SupportAgent
import json
from pathlib import Path
from src.agent.retriever import KnowledgeBase


def create_agent_without_model():
    agent = SupportAgent.__new__(SupportAgent)

    agent.knowledge_base = KnowledgeBase("knowledge-base")

    return agent


def test_agent_can_retrieve_company_content():
    agent = create_agent_without_model()

    results = agent.retrieve("What is the return policy?")

    assert results
    assert any(
        "return" in result.document.content.lower()
        for result in results
    )


def test_agent_can_use_order_lookup():
    agent = create_agent_without_model()

    with Path("data/orders.json").open("r", encoding="utf-8") as file:
        data = json.load(file)

    order_id = data["orders"][0]["order_id"]

    result = agent.lookup_order(order_id)

    assert result["found"] is True
    assert result["order"]["order_id"] == order_id

    assert "email" not in result["order"]
    assert "address" not in result["order"]
    assert "internal_notes" not in result["order"]
    assert "risk_score" not in result["order"]


def test_agent_keeps_conversation_context():
    agent = SupportAgent.__new__(SupportAgent)

    from src.agent.memory import ConversationMemory

    agent.memory = ConversationMemory()

    agent.add_message(
        "user",
        "Do you ship internationally?"
    )

    agent.add_message(
        "assistant",
        "Yes, international shipping is available."
    )

    agent.add_message(
        "user",
        "What about Canada?"
    )

    context = agent.get_context()

    assert len(context) == 3
    assert context[0]["content"] == "Do you ship internationally?"
    assert context[2]["content"] == "What about Canada?"

def test_agent_routes_order_questions_to_order_tool():
    agent = create_agent_without_model()

    assert agent.decide_action(
        "Where is my order?"
    ) == "order"


def test_agent_routes_policy_questions_to_knowledge_base():
    agent = create_agent_without_model()

    assert agent.decide_action(
        "What is your return policy?"
    ) == "knowledge"


def test_agent_does_not_guess_ambiguous_requests():
    agent = create_agent_without_model()

    assert agent.decide_action(
        "Can you help me?"
    ) == "unknown"

def test_handle_policy_question_returns_grounded_answer():
    agent = create_agent_without_model()

    result = agent.handle("What is the return policy?")

    assert result["action"] == "knowledge"
    assert result["answer"]
    assert result["sources"]


def test_handle_order_question_requests_order_id():
    agent = create_agent_without_model()

    result = agent.handle("Where is my order?")

    assert result["action"] == "order"
    assert "order ID" in result["answer"]


def test_handle_empty_message_is_safe():
    agent = create_agent_without_model()

    result = agent.handle("")

    assert result["action"] == "unknown"
    assert result["answer"]
    assert result["sources"] == []

def test_agent_response_contract():
    from src.agent.response import AgentResponse

    response = AgentResponse(
        answer="Your return window is 30 days.",
        action="knowledge",
        sources=["returns.md — Return Window"],
    )

    assert response.answer
    assert response.action == "knowledge"
    assert response.sources == ["returns.md — Return Window"]
    assert response.requires_input is False

def test_handle_order_with_order_id_uses_safe_lookup():
    agent = create_agent_without_model()

    with Path("data/orders.json").open("r", encoding="utf-8") as file:
        data = json.load(file)

    order_id = data["orders"][0]["order_id"]

    result = agent.handle(
        f"Can you check order {order_id}?"
    )

    assert result["action"] == "order"
    assert order_id in result["answer"]
    assert "email" not in result["answer"]
    assert "address" not in result["answer"]
    assert "internal_notes" not in result["answer"]
    assert "risk_score" not in result["answer"]


def test_handle_unknown_order_does_not_expose_data():
    agent = create_agent_without_model()

    result = agent.handle("Can you check order ORD-9999?")

    assert result["action"] == "order"
    assert "couldn't find" in result["answer"].lower()

def test_mock_model_generates_response():
    from src.agent.models import MockModel

    model = MockModel()

    result = model.generate("Hello")

    assert isinstance(result, str)
    assert result

def test_agent_can_generate_response_without_api_key():
    agent = SupportAgent()

    response = agent.generate_response("Say hello.")

    assert isinstance(response, str)
    assert response.strip()

def test_make_response_creates_standard_response():
    from src.agent.response import AgentResponse, make_response

    result = make_response(
        answer="Test answer",
        action="knowledge",
        sources=["source.md"],
        requires_input=False,
    )

    assert isinstance(result, AgentResponse)
    assert result.answer == "Test answer"
    assert result.action == "knowledge"
    assert result.sources == ["source.md"]
    assert result.requires_input is False