venv := venv
PYTHON := $(venv)/Scripts/python.exe  # Update path for Unix if needed
PIP := $(venv)/Scripts/pip            # Update path for Unix if needed

.PHONY: venv
venv:
	$(PYTHON) -m venv $(venv)
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

.PHONY: migrate
migrate:
	alembic upgrade head

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
	docker-compose down

.PHONY: docker-migrate
docker-migrate:
	docker-compose exec api alembic revision --autogenerate -m "Auto migration" || echo "No new migration"
	docker-compose exec api alembic upgrade head

.PHONY: clean
clean:
	rm -rf __pycache__ *.pyc *.pyo $(venv) model.pkl

.PHONY: reset-db
reset-db:
	rm -rf app/alembic
	rm -rf alembic.ini
	docker-compose exec api alembic init app/infrastructure/db/migrations
	docker-compose exec api alembic revision --autogenerate -m "Initial migration"
	docker-compose exec api alembic upgrade head

.PHONY: docker-logs
docker-logs:
	docker-compose logs -f

.PHONY: docker-restart
docker-restart:
	docker-compose restart

.PHONY: test
test:
	pytest tests/