venv := venv
PYTHON := $(venv)/Scripts/python.exe
PIP := $(venv)/Scripts/pip

.PHONY: venv
venv:
	python3 -m venv $(venv)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install
install: venv

.PHONY: run
run:
	venv/Scripts/uvicorn app.main:app --reload

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
	alembic revision --autogenerate -m "new migration"

.PHONY: docker-build
docker-build:
	docker build -t ml-api .

.PHONY: docker-run
docker-run:
	docker-compose up --build -d

.PHONY: docker-stop
docker-stop:
	docker-compose down  # Stop containers

.PHONY: docker-migrate
docker-migrate:
	docker-compose exec api alembic upgrade head

.PHONY: clean
clean:
	rm -rf __pycache__ *.pyc *.pyo $(venv) model.pkl

.PHONY: reset-db
reset-db:
	rm -rf app/infrastructure/db/migrations
	alembic init app/infrastructure/db/migrations

.PHONY: docker-logs
docker-logs:
	docker-compose logs -f

.PHONY: docker-restart
docker-restart:
	docker-compose restart  # Restart the services
