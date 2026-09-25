# Udatracker Order Management System

Minimal order-tracking backend built with **Test-Driven Development (TDD)** using Flask and pytest. A provided frontend consumes the REST API.

## Features

- Create orders (`POST /api/orders`)
- Get an order by ID (`GET /api/orders/<order_id>`)
- Update order status (`PUT /api/orders/<order_id>/status`)
- List all orders or filter by status (`GET /api/orders`, `GET /api/orders?status=pending`)
- In-memory storage (data resets when the server restarts)

## Project Structure

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Setup

```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
# source venv/bin/activate

pip install -r backend/requirements.txt
```

## Run the app

From the `starter/` directory:

```bash
python -m backend.app
```

Open http://127.0.0.1:5000

## Run tests

Always from `starter/`:

```bash
pytest
pytest backend/tests/test_order_tracker.py
pytest backend/tests/test_api.py
```

## Reflection

- **Design decision:** Business rules live in `OrderTracker`, while Flask routes only validate HTTP input, call tracker methods, and return JSON with status codes. That kept unit tests independent of the web layer and made integration tests focus on the API contract.
- **Testing insight:** Writing unit tests before the implementation forced clear error behavior (for example, duplicate IDs and invalid statuses). A failing update-status test clarified that missing orders should raise `KeyError` (mapped to 404) while bad input stays a `ValueError` (400).
- **Next step:** Add a `DELETE /api/orders/<order_id>` endpoint and replace in-memory storage with a database so orders survive server restarts.
