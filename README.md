# CRTRCOD

**This software does not guarantee profits. Trading involves significant risk of loss.**

## Overview
CRTRCOD is a modular, research-first cryptocurrency spot trading platform for data ingestion, feature engineering, strategy research, backtesting, paper trading, risk controls, and operator dashboards.

## Quickstart
```bash
uv sync
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d
uv run pytest tests/ -v
```


## Русское руководство
Подробная инструкция по архитектуре, запуску, risk engine, kill switch и live trading checklist доступна в [docs/manual_ru.md](docs/manual_ru.md). Если проект «не работает», начните с [docs/troubleshooting_ru.md](docs/troubleshooting_ru.md) и `python scripts/doctor.py`.

## v2 Stability
Stability checklist and operational validation steps are documented in [docs/v2_stability_plan.md](docs/v2_stability_plan.md).

## Architecture
The project is split into `packages/` for reusable domain modules and `apps/` for API, worker, and dashboard entrypoints. PostgreSQL stores operational records, Redis backs queues and kill-switch state, DuckDB/Parquet power research, and MLflow tracks experiments.

## Make commands
Common operator shortcuts are available in `Makefile`: `make doctor`, `make install`, `make lint`, `make type`, `make test`, `make api`, `make worker`, `make dashboard`, `make docker-up`, and `make docker-down`.

## Running Tests
```bash
uv run ruff check .
uv run mypy packages/ apps/ --ignore-missing-imports
uv run pytest tests/ -v
```

## Risk Disclaimer
See [RISK_DISCLAIMER.md](RISK_DISCLAIMER.md). This project is tooling, not financial advice.
