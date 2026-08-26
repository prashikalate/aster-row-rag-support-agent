import json
from pathlib import Path

from src.agent.orders import lookup_order


ORDERS_PATH = "data/orders.json"


def get_real_order_id():
    with Path(ORDERS_PATH).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data[0]["order_id"]

    if isinstance(data, dict) and isinstance(data.get("orders"), list):
        return data["orders"][0]["order_id"]

    if isinstance(data, dict):
        return next(iter(data.keys()))

    raise AssertionError("Unsupported orders.json format")


def test_valid_order_lookup():
    order_id = get_real_order_id()

    result = lookup_order(order_id)

    assert result["found"] is True
    assert result["order"]["order_id"] == order_id


def test_order_id_is_normalized():
    order_id = get_real_order_id()

    result = lookup_order(f"  {order_id.lower()}  ")

    assert result["found"] is True
    assert result["order"]["order_id"] == order_id


def test_unknown_order_is_safe():
    result = lookup_order("ORD-9999")

    assert result["found"] is False
    assert "error" in result


def test_malformed_order_id_is_rejected():
    result = lookup_order("hello")

    assert result["found"] is False
    assert "error" in result


def test_private_fields_are_not_exposed():
    order_id = get_real_order_id()

    result = lookup_order(order_id)

    assert result["found"] is True

    order = result["order"]

    forbidden_fields = {
        "email",
        "customer_email",
        "address",
        "internal_notes",
        "notes",
        "risk_score",
    }

    assert forbidden_fields.isdisjoint(order.keys())


def test_cancelled_or_returned_orders_do_not_show_delivery_estimate():
    with Path(ORDERS_PATH).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        orders = data
    elif isinstance(data, dict) and isinstance(data.get("orders"), list):
        orders = data["orders"]
    elif isinstance(data, dict):
        orders = list(data.values())
    else:
        orders = []

    for order in orders:
        status = str(order.get("status", "")).lower()

        if status in {"cancelled", "returned"}:
            result = lookup_order(order["order_id"])

            assert result["found"] is True
            assert "estimated_delivery" not in result["order"]

def test_order_tool_uses_safe_lookup():
    from src.agent.orders import order_tool

    order_id = get_real_order_id()
    result = order_tool(order_id)

    assert result["found"] is True
    assert "email" not in result["order"]
    assert "address" not in result["order"]
    assert "internal_notes" not in result["order"]
    assert "risk_score" not in result["order"]

def test_extract_order_id_from_customer_message():
    from src.agent.orders import extract_order_id

    assert extract_order_id(
        "Can you check order ord-1007?"
    ) == "ORD-1007"


def test_extract_order_id_returns_none_when_missing():
    from src.agent.orders import extract_order_id

    assert extract_order_id(
        "Where is my package?"
    ) is None