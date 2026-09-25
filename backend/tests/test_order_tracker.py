import pytest
from unittest.mock import Mock, call
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- Unit tests for OrderTracker ---
#

def test_add_order_success_defaults_to_pending(order_tracker, mock_storage):
    result = order_tracker.add_order("ORD001", "Laptop", 2, "CUST001")

    assert result["order_id"] == "ORD001"
    assert result["item_name"] == "Laptop"
    assert result["quantity"] == 2
    assert result["customer_id"] == "CUST001"
    assert result["status"] == "pending"
    mock_storage.save_order.assert_called_once_with("ORD001", result)


def test_add_order_with_explicit_status(order_tracker, mock_storage):
    result = order_tracker.add_order(
        "ORD002", "Phone", 1, "CUST002", status="processing"
    )

    assert result["status"] == "processing"
    mock_storage.save_order.assert_called_once()


def test_add_order_duplicate_id_raises(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="already exists"):
        order_tracker.add_order("ORD001", "Tablet", 1, "CUST002")

    mock_storage.save_order.assert_not_called()


def test_add_order_invalid_quantity_raises(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order("ORD003", "Mouse", 0, "CUST003")

    mock_storage.save_order.assert_not_called()


def test_add_order_missing_required_field_raises(order_tracker, mock_storage):
    with pytest.raises(ValueError):
        order_tracker.add_order("", "Keyboard", 1, "CUST004")

    mock_storage.save_order.assert_not_called()


def test_get_order_by_id_success(order_tracker, mock_storage):
    existing = {
        "order_id": "ORD010",
        "item_name": "Monitor",
        "quantity": 1,
        "customer_id": "CUST010",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing

    result = order_tracker.get_order_by_id("ORD010")

    assert result == existing
    mock_storage.get_order.assert_called_with("ORD010")


def test_get_order_by_id_not_found(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    assert order_tracker.get_order_by_id("MISSING") is None


def test_get_order_by_id_empty_id_raises(order_tracker):
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("")


def test_update_order_status_success(order_tracker, mock_storage):
    existing = {
        "order_id": "ORD020",
        "item_name": "Headset",
        "quantity": 1,
        "customer_id": "CUST020",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing.copy()

    result = order_tracker.update_order_status("ORD020", "shipped")

    assert result["status"] == "shipped"
    mock_storage.save_order.assert_called_once()
    saved_id, saved_data = mock_storage.save_order.call_args[0]
    assert saved_id == "ORD020"
    assert saved_data["status"] == "shipped"


def test_update_order_status_not_found_raises(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    with pytest.raises(KeyError, match="not found"):
        order_tracker.update_order_status("MISSING", "shipped")


def test_update_order_status_invalid_status_raises(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD021",
        "item_name": "Cable",
        "quantity": 1,
        "customer_id": "CUST021",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD021", "delivered")


def test_update_order_status_empty_order_id_raises(order_tracker):
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status("", "shipped")


def test_list_all_orders(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "A1": {
            "order_id": "A1",
            "item_name": "Item A",
            "quantity": 1,
            "customer_id": "C1",
            "status": "pending",
        },
        "B1": {
            "order_id": "B1",
            "item_name": "Item B",
            "quantity": 2,
            "customer_id": "C2",
            "status": "shipped",
        },
    }

    result = order_tracker.list_all_orders()

    assert len(result) == 2
    assert {order["order_id"] for order in result} == {"A1", "B1"}


def test_list_orders_by_status(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "A1": {
            "order_id": "A1",
            "item_name": "Item A",
            "quantity": 1,
            "customer_id": "C1",
            "status": "pending",
        },
        "B1": {
            "order_id": "B1",
            "item_name": "Item B",
            "quantity": 2,
            "customer_id": "C2",
            "status": "shipped",
        },
        "C1": {
            "order_id": "C1",
            "item_name": "Item C",
            "quantity": 3,
            "customer_id": "C3",
            "status": "pending",
        },
    }

    result = order_tracker.list_orders_by_status("pending")

    assert len(result) == 2
    assert all(order["status"] == "pending" for order in result)


def test_list_orders_by_status_invalid_raises(order_tracker):
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("")
