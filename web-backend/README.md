# FormFusion Backend

FastAPI backend for secure multi-phone sessions, live pose-frame synchronization,
triangulation, filtering, joint angles, rep counting, and dashboard broadcasts.

## Run locally

```powershell
cd web-backend
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
.venv\Scripts\uvicorn.exe formfusion.main:app --reload
```

Or run with Docker:

```powershell
docker compose up --build
```

OpenAPI is available at `/docs`, metrics at `/metrics`, and health checks at
`/health/live` and `/health/ready`.

## Verify

```powershell
python -m pytest
ruff check .
mypy src
```

See [BACKEND_ARCHITECTURE_PLAN.md](BACKEND_ARCHITECTURE_PLAN.md) and
[docs/protocol.md](docs/protocol.md) for architecture and wire contracts.

