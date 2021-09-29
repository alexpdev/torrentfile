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

environment:
	.\env\Scripts\activate.bat

clean-build: ## remove build artifacts
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

test: environment ## run tests quickly with the default Python
	pytest tests

coverage: clean environment test ## check code coverage with the default Python
	coverage run -m pytest tests
	coverage xml -o corbertura.xml
	git add .
	git commit -m "coverage report bug and linting adjustments pass all tests"
	git push
	bash codacy.sh report -r corbertura.xml

release: install ## package and upload a release
	rm -rf ..\tfilexe
	mkdir ..\tfilexe
	cp -f env\scripts\tfile ..\tfilexe
	pyinstaller -c -n torrentfile --workpath ..\tfilexe\build --distpath ..\tfilexe\dist -i .\assets\torrentfile.ico -F ..\tfilexe\tfile
	python setup.py sdist bdist_egg bdist_wheel
	twine upload dist/*
	make coverage

checkout: ## push to remote
	git add .
	git commit -m "auto commit and publish"
	git push

start: clean ## start new branch
	git branch development
	git checkout development
	git push --set-upstream origin development

lint: ## lint errors
	pylama torrentfile tests

install: environment clean test ## Install Locally
	python setup.py install




full: clean test checkout coverage
