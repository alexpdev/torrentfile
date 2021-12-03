.PHONY: clean help full lint build environment test docs push
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

define FIX_BIN_VERSION_FILES
import os
from pathlib import Path
from torrentfile.version import __version__ as version

for item in Path("./dist").iterdir():
	if item.suffix in [".exe", ".zip"]:
		newname = f"{item.stem}{version}.winx64{item.suffix}"
		full = item.parent / newname
		os.rename(item, full)
endef
export FIX_BIN_VERSION_FILES

BROWSER := python -c "$$BROWSER_PYSCRIPT"


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build ## remove all build, test, coverage and Python artifacts

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

lint: ## Check for styling errors
	@echo Linting
	autopep8 --recursive torrentfile tests
	isort torrentfile tests
	pydocstyle torrentfile tests
	pycodestyle torrentfile tests
	pylint torrentfile tests
	pyroma .
	prospector torrentfile
	prospector tests

test: lint ## run tests quickly with the default Python
	@echo Testing
	pytest --cov=torrentfile --cov=tests --pylint tests
	coverage xml -o coverage.xml

push: clean lint test docs ## push to remote repo
	@echo pushing to remote
	git add .
	git commit -m "$m"
	git push
	bash codacy.sh report -r coverage.xml

docs: ## Regenerate docs from changes
	rm -rf docs/*
	mkdocs -q build
	touch docs/.nojekyll

build: clean install
	python setup.py sdist bdist_wheel bdist_egg
	rm -rfv ../runner
	mkdir ../runner
	touch ../runner/exe
	cp ./assets/favicon.ico ../runner/favicon.ico
	@echo "import torrentfile" >> ../runner/exe
	@echo "torrentfile.main()" >> ../runner/exe
	pyinstaller --distpath ../runner/dist --workpath ../runner/build \
		-F -n torrentfile -c -i ../runner/favicon.ico \
		--specpath ../runner/ ../runner/exe
	pyinstaller --distpath ../runner/dist --workpath ../runner/build \
		-D -n torrentfile -c -i ../runner/favicon.ico \
		--specpath ../runner/ ../runner/exe
	cp -rfv ../runner/dist/* ./dist/
	python -c "$$FIX_BIN_VERSION_FILES"

install: ## Install Locally
	pip install --upgrade -rrequirements.txt --no-cache-dir --pre
	pip install -e .

branch: clean ## Switch git branches after changes have been made
	git checkout master
	git pull
	git branch -d dev
	git branch dev
	git checkout dev
	git push -u origin dev
