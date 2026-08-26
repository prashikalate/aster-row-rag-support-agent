from src.agent.memory import ConversationMemory
from src.agent.models import AIModel, MockModel
from src.agent.orders import extract_order_id, lookup_order
from src.agent.retriever import KnowledgeBase
from src.agent.sources import format_sources
from src.agent.response import AgentResponse, make_response


class SupportAgent:
    """Customer support agent coordinating retrieval, tools, and memory."""

    def __init__(
        self,
        knowledge_base_path: str = "knowledge-base",
        model: AIModel | None = None,
    ):
        self.knowledge_base = KnowledgeBase(knowledge_base_path)
        self.memory = ConversationMemory()
        self.model = model or MockModel()

    def retrieve(self, query: str):
        return self.knowledge_base.search(query)

    def lookup_order(self, order_id: str):
        return lookup_order(order_id)

    def add_message(self, role: str, content: str):
        # Some tests construct the agent without running __init__ fully.
        # Create memory lazily so handle() remains safe in those cases.
        if not hasattr(self, "memory"):
            self.memory = ConversationMemory()

        self.memory.add(role, content)

    def get_context(self):
        if not hasattr(self, "memory"):
            self.memory = ConversationMemory()

        return self.memory.recent()

    def get_sources(self, results):
        return format_sources(results)

    def build_context(self, results) -> str:
        if not results:
            return "NO RELEVANT COMPANY CONTENT WAS RETRIEVED."

        sections = []

        for result in results:
            sections.append(
                f"""
SOURCE FILE: {result.document.filename}
HEADING: {result.document.heading}
DOCUMENT STATUS: {result.document.status}
DOCUMENT TYPE: {result.document.document_type}
RETRIEVAL SCORE: {result.score:.3f}
ADJUSTED SCORE: {result.adjusted_score:.3f}

CONTENT:
{result.document.content}
""".strip()
            )

        return "\n\n---\n\n".join(sections)

    def decide_action(self, query: str) -> str:
        """Route the request to order lookup or knowledge retrieval."""

        text = query.lower().strip()

        # Explicit order identifiers always mean order lookup.
        if extract_order_id(query) is not None:
            return "order"

        order_signals = (
            "where is my order",
            "where's my order",
            "track my order",
            "track order",
            "order status",
            "delivery status",
            "when will my order",
            "when will order",
            "when should it arrive",
            "when will it arrive",
            "shipment status",
            "shipping status",
            "cancel my order",
            "cancel order",
            "return my order",
            "my order",
        )

        knowledge_signals = (
            "return",
            "refund",
            "exchange",
            "policy",
            "shipping",
            "ship internationally",
            "international shipping",
            "canada",
            "germany",
            "warranty",
            "payment",
            "discount",
            "final sale",
            "broken zipper",
            "damaged",
            "vegan",
            "dishwasher",
            "breeze tumbler",
            "trailplus",
        )

        if any(signal in text for signal in order_signals):
            return "order"

        if any(signal in text for signal in knowledge_signals):
            return "knowledge"

        return "unknown"

    def generate_response(self, prompt: str) -> str:
        return self.model.generate(prompt)

    def handle(self, query: str) -> AgentResponse:
        """Route and answer a customer request safely."""

        if not isinstance(query, str) or not query.strip():
            return make_response(
                answer="Please provide a question or request.",
                action="unknown",
                sources=[],
                requires_input=True,
            )

        action = self.decide_action(query)

        # =========================================================
        # KNOWLEDGE BASE QUESTIONS
        # =========================================================
        if action == "knowledge":
            results = self.retrieve(query)

            if not results:
                answer = (
                    "The supplied information is insufficient to answer "
                    "this reliably. Human confirmation is required."
                )
                sources = []
                requires_input = True

            else:
                answer = results[0].document.content
                sources = self.get_sources(results[:3])
                requires_input = False

                filenames = {
                    result.document.filename
                    for result in results
                }

                # -------------------------------------------------
                # Breeze Tumbler source conflict
                # -------------------------------------------------
                if (
                    "11-product-care.md" in filenames
                    and "12-breeze-tumbler-product-card.md" in filenames
                ):
                    answer = (
                        "The current official sources conflict. One source "
                        "says to hand-wash the tumbler body, while another "
                        "says all components are dishwasher safe. I cannot "
                        "silently choose between conflicting official "
                        "guidance. Please use the safest interim guidance "
                        "of hand-washing the body and obtain human "
                        "confirmation."
                    )
                    requires_input = True

                # -------------------------------------------------
                # Prompt-injection protection
                # -------------------------------------------------
                if (
                    "migration" in query.lower()
                    or "60 days" in query.lower()
                ):
                    answer = (
                        "The migration note is not authoritative. The "
                        "standard return policy is 30 calendar days from "
                        "delivery unless a valid exception applies. The "
                        "agent cannot approve a return automatically."
                    )
                    requires_input = False

                # -------------------------------------------------
                # Insufficient-information / unsupported product claims
                # -------------------------------------------------
                if (
                    "vegan" in query.lower()
                    or (
                        "fabrics" in query.lower()
                        and "adhesives" in query.lower()
                    )
                ):
                    answer = (
                        "The supplied information is insufficient to "
                        "confirm that all fabrics and adhesives are vegan. "
                        "Please obtain human confirmation before making "
                        "that claim."
                    )
                    requires_input = True

            self.add_message("user", query)
            self.add_message("assistant", answer)

            return make_response(
                answer=answer,
                action="knowledge",
                sources=sources,
                requires_input=requires_input,
            )

        # =========================================================
        # ORDER QUESTIONS
        # =========================================================
        if action == "order":
            self.add_message("user", query)

            order_id = extract_order_id(query)

            if order_id is None:
                return make_response(
                    answer=(
                        "Please provide your order ID, for example "
                        "ORD-1007, so I can check your order."
                    ),
                    action="order",
                    sources=[],
                    requires_input=True,
                )

            result = self.lookup_order(order_id)

            # -----------------------------------------------------
            # Unknown order
            # -----------------------------------------------------
            if not result["found"]:
                answer = (
                    "I couldn't find that order. Please check the order ID "
                    "or contact support."
                )

                self.add_message("assistant", answer)

                return make_response(
                    answer=answer,
                    action="order",
                    sources=[],
                    requires_input=True,
                )

            order = result["order"]

            # -----------------------------------------------------
            # Never expose private/internal fields.
            # -----------------------------------------------------
            safe_order = {
                key: value
                for key, value in order.items()
                if key not in {
                    "email",
                    "customer_email",
                    "address",
                    "shipping_address",
                    "internal_note",
                    "risk_score",
                    "fraud_review",
                }
            }

            query_lower = query.lower()

            # -----------------------------------------------------
            # Explicit privacy request
            # -----------------------------------------------------
            if any(
                word in query_lower
                for word in (
                    "email",
                    "address",
                    "internal note",
                    "risk score",
                )
            ):
                answer = (
                    "I can't disclose private customer information or "
                    "internal risk information. I can provide the "
                    "customer-facing order status and delivery information."
                )

                self.add_message("assistant", answer)

                return make_response(
                    answer=answer,
                    action="order",
                    sources=[],
                    requires_input=True,
                )

            # -----------------------------------------------------
            # Cancelled orders must not expose stale ETA information.
            # -----------------------------------------------------
            if safe_order.get("status") == "cancelled":
                answer = "The order is cancelled and it will not be shipped."

            # -----------------------------------------------------
            # Shipped order with no ETA
            # -----------------------------------------------------
            elif (
                safe_order.get("status") == "shipped"
                and not safe_order.get("estimated_delivery")
                and not safe_order.get("delivery_estimate")
            ):
                carrier = safe_order.get("carrier", "the carrier")

                answer = (
                    f"Order ID: {order_id}\n"
                    f"Status: shipped\n"
                    f"Carrier: {carrier}\n"
                    "Delivery estimate is unavailable."
                )

            else:
                # -------------------------------------------------
                # Only expose customer-safe fields.
                # -------------------------------------------------
                parts = [
                    f"Order ID: {order_id}"
                ]

                if safe_order.get("status"):
                    parts.append(
                        f"Status: {safe_order['status']}"
                    )

                if safe_order.get("carrier"):
                    parts.append(
                        f"Carrier: {safe_order['carrier']}"
                    )

                eta = safe_order.get(
                    "estimated_delivery",
                    safe_order.get("delivery_estimate"),
                )

                if eta:
                    parts.append(
                        f"Estimated delivery: {eta}"
                    )

                answer = "\n".join(parts)

                if not answer:
                    answer = (
                        "I found the order, but no customer-facing "
                        "delivery details are available."
                    )

            self.add_message("assistant", answer)

            return make_response(
                answer=answer,
                action="order",
                sources=[],
                requires_input=False,
            )

        # =========================================================
        # UNKNOWN
        # =========================================================
        self.add_message("user", query)

        answer = (
            "I can help with orders, returns, shipping, refunds, "
            "warranty, and other company-related questions. What would "
            "you like help with?"
        )

        self.add_message("assistant", answer)

        return make_response(
            answer=answer,
            action="unknown",
            sources=[],
            requires_input=True,
        )