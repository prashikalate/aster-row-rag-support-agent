import json
import re
from pathlib import Path
from typing import Any


ORDER_ID_PATTERN = re.compile(r"^ORD-\d{4}$")

PUBLIC_FIELDS = {
    "order_id",
    "status",
    "items",
    "estimated_delivery",
}


def load_orders(path: str = "data/orders.json") -> dict[str, dict[str, Any]]:
    """Load orders and index them by order ID."""

    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        orders = data

    elif isinstance(data, dict) and isinstance(data.get("orders"), list):
        orders = data["orders"]

    else:
        raise ValueError("Unsupported orders.json format")

    return {
        order["order_id"]: order
        for order in orders
        if isinstance(order, dict) and "order_id" in order
    }
    """Load orders from the supplied JSON file."""

    with Path(path).open("r", encoding="utf-8") as file:
        orders = json.load(file)

    if isinstance(orders, list):
        return {
            order["order_id"]: order
            for order in orders
            if "order_id" in order
        }

    if isinstance(orders, dict):
        return orders

    raise ValueError("Unsupported orders.json format")


def normalize_order_id(order_id: str) -> str:
    """Normalize harmless differences in user input."""

    return order_id.strip().upper()


def sanitize_order(order: dict[str, Any]) -> dict[str, Any]:
    """Return only fields that are safe for customer-facing responses."""

    result = {
        field: order[field]
        for field in PUBLIC_FIELDS
        if field in order
    }

    status = str(result.get("status", "")).lower()

    if status in {"cancelled", "returned"}:
        result.pop("estimated_delivery", None)

    return result


def lookup_order(
    order_id: str,
    orders_path: str = "data/orders.json",
) -> dict[str, Any]:
    """Safely look up one order."""

    if not isinstance(order_id, str):
        return {
            "found": False,
            "error": "Order ID must be text.",
        }

    normalized_id = normalize_order_id(order_id)

    if not ORDER_ID_PATTERN.fullmatch(normalized_id):
        return {
            "found": False,
            "error": "Invalid order ID format.",
        }

    orders = load_orders(orders_path)

    order = orders.get(normalized_id)

    if order is None:
        return {
            "found": False,
            "error": "Order not found.",
            "order_id": normalized_id,
        }

    return {
        "found": True,
        "order": sanitize_order(order),
    }

def order_tool(order_id: str) -> dict[str, Any]:
    """
    Customer-facing order lookup tool.

    Only sanitized order information is returned.
    """

    return lookup_order(order_id)

def extract_order_id(text: str) -> str | None:
    """Extract a valid order ID from customer text."""

    if not isinstance(text, str):
        return None

    match = re.search(r"\bORD-\d{4}\b", text.upper())

    if match is None:
        return None

    return match.group(0)