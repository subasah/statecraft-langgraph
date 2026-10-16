.PHONY: help install test cli ui api docs clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
STREAMLIT = $(VENV)/bin/streamlit
UVICORN = $(VENV)/bin/uvicorn

help:
	@echo "StateCraft - Commands:"
	@echo "  make install   - Install dependencies and statecraft package"
	@echo "  make test      - Run all 14 unit and integration tests"
	@echo "  make cli       - Launch the interactive Rich terminal CLI"
	@echo "  make ui        - Launch the Streamlit visual playground"
	@echo "  make api       - Start the FastAPI REST server"
	@echo "  make docs      - Open the interactive web documentation in default browser"
	@echo "  make clean     - Clean caches and build artifacts"

install:
	uv pip install -e .

test:
	$(PYTEST) tests/ -v

cli:
	$(PYTHON) -m statecraft.cli

ui:
	$(STREAMLIT) run streamlit_app.py

api:
	$(UVICORN) statecraft.api:app --reload --port 8000

docs:
	open docs/index.html

clean:
	rm -rf .pytest_cache build dist src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
