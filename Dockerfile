FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY backend/ backend/
COPY frontend/dist/ frontend/dist/

RUN pip install uv && uv sync --no-dev

EXPOSE 7860

CMD uv run uvicorn backend.api:app --host 0.0.0.0 --port 7860 & uv run python -m http.server 7860 --directory frontend/dist
