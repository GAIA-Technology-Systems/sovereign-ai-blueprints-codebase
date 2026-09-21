.PHONY: help test lint demo evals clean

help:
	@echo "make test    - run the test suite"
	@echo "make demo    - run all three scenarios offline (mock client)"
	@echo "make evals   - run the eval harness, including leakage canaries"
	@echo "make lint    - ruff"

test:
	pytest -q

lint:
	ruff check src tests scenarios evals

demo:
	@echo "--- scenario 1: internal knowledge assistant (tier 1) ---"
	@python scenarios/scenario1_docs_assistant/run.py
	@echo "\n--- scenario 2: claims assist (tier 2) ---"
	@python scenarios/scenario2_claims_assist/run.py
	@echo "\n--- scenario 3: correspondence triage (tier 3) ---"
	@python scenarios/scenario3_correspondence/run.py
	@echo "\n--- which tier? ---"
	@python -m sovereign.cli which-tier --personal-data --eu-only-contract

evals:
	python evals/run_evals.py

clean:
	rm -rf var .pytest_cache **/__pycache__
