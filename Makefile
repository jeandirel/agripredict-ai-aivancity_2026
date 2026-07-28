.PHONY: install frontend-install audit train final test lint quality api dashboard dashboard-legacy frontend-test frontend-lint frontend-build reproduce docker-up docker-down

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"
	npm --prefix frontend ci

frontend-install:
	npm --prefix frontend ci

audit:
	python scripts/audit_phase0.py

train:
	python scripts/train_models.py --output artifacts/models --report-dir reports/modeling

final:
	python scripts/finalize_project.py --output artifacts/models --report-dir reports/final
	pytest --cov=src/agripredict --cov=app/api --cov-report=term-missing
	ruff check src app scripts tests

test:
	pytest --cov=src/agripredict --cov=app/api --cov-report=term-missing

lint:
	ruff check src app scripts tests

quality: lint test frontend-lint frontend-test frontend-build

api:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	npm --prefix frontend run dev -- --host 0.0.0.0 --port 8501

dashboard-legacy:
	streamlit run app/dashboard/app.py

frontend-test:
	npm --prefix frontend run test

frontend-lint:
	npm --prefix frontend run lint

frontend-build:
	npm --prefix frontend run build

reproduce: audit final

docker-up:
	docker compose up --build

docker-down:
	docker compose down
