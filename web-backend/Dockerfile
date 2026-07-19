FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system formfusion && adduser --system --ingroup formfusion formfusion

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && python -m pip install .

USER formfusion
EXPOSE 8000

CMD ["uvicorn", "formfusion.main:app", "--host", "0.0.0.0", "--port", "8000", "--ws-max-size", "262144", "--timeout-keep-alive", "10"]

