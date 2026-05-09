# Logistics Assistant - Backend

FastAPI service providing product catalog and logistics tools.

## Setup

1. **Environment**: Create and activate a Python 3.12+ virtual environment using your preferred tool (venv, pyenv, conda, etc.).

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Data Preparation**:
   The products are seeded from a CSV file into a local SQLite database on startup. To regenerate the CSV with specialized brand data:
   ```bash
   python backend/generate_products.py
   ```

## Running the Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.
Swagger documentation: `http://localhost:8000/docs`.

## API Endpoints

- `GET /health`: Basic health check.
- `GET /products?query={name}`: Search products by name (case-insensitive).
- `POST /shipping/quote`: Calculate shipping costs for multiple providers.
- `POST /packaging/optimize`: Suggest box sizes for a set of items.
