.PHONY: clean help full
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build ## remove all build, test, coverage and Python artifacts

environment: ## environment
	.\env\Scripts\activate.bat

clean-build: ## remove build artifacts
	@echo Cleaning
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .tox/
	rm -f .coverage
	rm -rf */__pycache__
	rm -fr htmlcov/
	rm -rf *.egg-info
	rm -f corbertura.xml
	rm -fr .pytest_cache
	rm -f *.spec

lint: environment ## Check for styling errors
	@echo Linting
	autopep8 --recursive torrentfile tests
	isort torrentfile tests
	pydocstyle torrentfile tests
	pyroma .
	pylint torrentfile tests
	prospector torrentfile
	prospector tests


test: environment ## run tests quickly with the default Python
	@echo Testing
	pytest tests --cov --pylint

coverage: environment ## check code coverage with the default Python
	@echo Generating Coverage Report
	coverage run -m pytest tests
	coverage xml -o coverage.xml

push: clean lint test coverage docs ## push to remote repo
	@echo pushing to remote
	git add .
	git commit -m "$m"
	git push -u dev master
	bash codacy.sh report -r coverage.xml

docs: environment ## Regenerate docs from changes
	rm -rf docs/*
	mkdocs -q build
	touch docs/.nojekyll

install: environment clean test ## Install Locally
	python setup.py install
