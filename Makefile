.PHONY: clean help test docs release
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

define UPDATE_PACKAGE_VERSION
import json
from torrentfile.version import __version__
data = json.load(open("package.json"))
if data['version'] != __version__:
	data['version'] = __version__
	json.dump(data, open("package.json", "wt"), indent=2)
endef
export UPDATE_PACKAGE_VERSION

define RENAME_FILE
from torrentfile.version import __version__
import os
import sys
if sys.platform == "win32":
	inexe = "./torrentfile-windows-exec.zip"
	exe = f"./dist/torrentfile-v{__version__}-win-exe.zip"
	indir = "./torrentfile-windows-dir.zip"
	dir = f"./dist/torrentfile-v{__version__}-win-dir.zip"
	os.rename(inexe, exe)
	os.rename(indir, dir)
endef
export RENAME_FILE

BROWSER := python -c "$$BROWSER_PYSCRIPT"

RENAME := python -c "$$RENAME_FILE"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@echo Cleaning
	rm -rf build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .tox/
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -f corbertura.xml
	rm -fr .pytest_cache
	rm -rf Release
	rm -rf *.egg-info
	rm -rf .benchmarks
	rm -rf .codacy-coverage
	rm -rf node_modules
	rm -f torrentfile.log
	rm -fr -- *'/__pycache__'
	rm -fr runner/build
	rm -fr runner/dist
	rm -rf *.zip
	rm -f *.spec

test: ## Get coverage report
	tox

docs: ## Regenerate docs from changes
	rm -rf docs/*
	rm -rf site/index.md
	cp -rf README.md site/index.md
	cp -rf CHANGELOG.md site/changelog.md
	rm -rf site/htmlcov
	mv -f htmlcov site/
	mkdocs build
	touch docs/.nojekyll

push: clean test docs ## Push to github
	git add .
	git commit -m "$m"
	git push

setup: clean ## setup and build repo
	python setup.py sdist bdist_wheel
	pip install -e .
	twine upload dist/*

compile: clean test ## compile application for distribution
	pip install pyinstaller
	pip install -e .
	pyinstaller -F --name torrentfile --icon ./assets/torrentfile-icon.ico ./bin/torrentfile
	pyinstaller --name torrentfile --icon ./assets/torrentfile-icon.ico ./bin/torrentfile
	7z a ./torrentfile-windows-exec.zip ./dist/torrentfile.exe
	7z a ./torrentfile-windows-dir.zip ./dist/torrentfile
	python -c "$$RENAME_FILE"
