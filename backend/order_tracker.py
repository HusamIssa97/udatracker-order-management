# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = {"pending", "processing", "shipped"}


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def _validate_required_string(self, value, field_name: str):
        if value is None or not str(value).strip():
            raise ValueError(f"{field_name} is required")

    def _validate_status(self, status: str):
        if not status or status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Allowed values: {', '.join(sorted(VALID_STATUSES))}")

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        self._validate_required_string(order_id, "order_id")
        self._validate_required_string(item_name, "item_name")
        self._validate_required_string(customer_id, "customer_id")

        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError("quantity must be a positive integer")

        self._validate_status(status)

        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with id '{order_id}' already exists")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        self._validate_required_string(order_id, "order_id")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        self._validate_required_string(order_id, "order_id")
        self._validate_status(new_status)

        order = self.storage.get_order(order_id)
        if order is None:
            raise KeyError(f"Order '{order_id}' not found")

        order["status"] = new_status
        self.storage.save_order(order_id, order)
        return order

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        self._validate_status(status)
        return [order for order in self.list_all_orders() if order.get("status") == status]
