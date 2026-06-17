.PHONY: doctor install lint type test compile api worker dashboard docker-up docker-down

doctor:
	python scripts/doctor.py

install:
	uv sync

lint:
	uv run ruff check .

type:
	uv run mypy packages/ apps/ --ignore-missing-imports

test:
	uv run pytest tests/ -v

compile:
	python -m py_compile $$(find packages apps -name '*.py')

api:
	uv run uvicorn apps.api.main:app --reload

worker:
	uv run celery -A apps.worker.celery_app worker --loglevel=info

dashboard:
	uv run streamlit run apps/dashboard/main.py

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down
