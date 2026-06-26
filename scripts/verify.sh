#!/usr/bin/env bash
# Roda a suíte completa de verificação do janus-client: testes, cobertura,
# checagem de tipos e lint. Para no primeiro erro.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/4 pytest"
uv run python -m pytest -q

echo "==> 2/4 pytest --cov"
uv run python -m pytest --cov=src/janus_client --cov-report=term-missing -q

echo "==> 3/4 mypy"
uv run python -m mypy src/

echo "==> 4/4 ruff"
uv run ruff check src/ tests/

echo "==> tudo verde"
