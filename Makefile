venv := venv
PYTHON := $(venv)/bin/python3.10
PIP := $(venv)/bin/pip

.PHONY: venv

venv:
	python3 -m venv $(venv)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install
install: venv

.PHONY: run
run:
	venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # Windows

.PHONY: format
format:
	black .

.PHONY: lint
lint:
	flake8 .  

.PHONY: test
test:
	pytest tests/

.PHONY: docker-build
docker-build:
	docker build -t ml-api .

.PHONY: docker-run
docker-run:
	docker run -p 8000:8000 ml-api

.PHONY: clean
clean:
	rm -rf __pycache__ *.pyc *.pyo $(venv) model.pkl