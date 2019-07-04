.PHONY: all test type-check lint unit-test unit-test-with-coverage integration-test

all: test

test: type-check lint unit-test-with-coverage

type-check:
	@echo [mypy] Type checking ... 
	@mypy leetcode

lint:
	@echo [pylint] Checking coding style ...
	@tools/run-pylint.sh

unit-test:
	@echo [unittest] Running unit tests ...
	@python3 -m unittest discover "." "test_*.py" -v

unit-test-with-coverage:
	@echo [unittest+coverage] Running unit tests with coverage ...
	@coverage run -m unittest discover "." "test_*.py" -v
	@coverage report || (echo Under minimum required coverage && false)

integration-test:
	@echo [unittest] Running integration tests ...
	@python3 -m unittest discover "." "integration_*.py" -v
