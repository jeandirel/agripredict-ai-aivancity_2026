.PHONY: install audit train test lint api dashboard reproduce

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

audit:
	python scripts/audit_phase0.py

train:
	python scripts/train_models.py --output artifacts/models --report-dir reports/modeling

test:
	pytest --cov=src/agripredict --cov=app/api --cov-report=term-missing

lint:
	ruff check src app scripts tests

api:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run app/dashboard/app.py

reproduce: audit train test
