venv := venv
PYTHON := $(venv)/Scripts/python.exe
PIP := $(venv)/Scripts/pip

.PHONY: venv
venv:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install
install: venv

.PHONY: run
run:
	venv/Scripts/uvicorn app.infrastructure.entrypoints.api:app --host 0.0.0.0 --port 8000 --reload  # Windows/Linux

.PHONY: format
format:
	black .
	isort .

.PHONY: lint
lint:
	flake8 .  

.PHONY: test
test:
	pytest tests/

.PHONY: migrate
migrate:
	alembic upgrade head  # Apply migrations

.PHONY: makemigrations
makemigrations:
	alembic revision --autogenerate -m "new migration"  # Create new migration

.PHONY: docker-build
docker-build:
	docker build -t ml-api .

.PHONY: docker-run
docker-run:
	docker run --env-file .env -p 8000:8000 ml-api

.PHONY: clean
clean:
	rm -rf __pycache__ *.pyc *.pyo $(venv) model.pkl

.PHONY: reset-db
reset-db:
	rm -rf app/infrastructure/db/migrations
	alembic init app/infrastructure/db/migrations
