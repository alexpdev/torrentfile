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
	rm -rvf build/
	rm -fvr dist/
	rm -fvr .eggs/
	rm -fvr .tox/
	rm -fv .coverage
	rm -fv coverage.xml
	rm -fvr htmlcov/
	rm -fv corbertura.xml
	rm -fvr .pytest_cache
	rm -rvf Release
	rm -rfv *.egg-info
	rm -rfv .benchmarks
	rm -rfv .codacy-coverage
	rm -rfv node_modules
	rm -fv torrentfile.log
	rm -fvr -- *'/__pycache__'
	rm -frv runner/build
	rm -frv runner/dist
	rm -rfv *.zip
	rm -fv *.spec

test: ## Get coverage report
	tox

docs: ## Regenerate docs from changes
	rm -rfv docs/*
	rm -rfv site/index.md
	cp -rfv README.md site/index.md
	cp -rfv CHANGELOG.md site/changelog.md
	rm -rfv site/htmlcov
	mv -fv htmlcov site/
	mkdocs build
	touch docs/.nojekyll

push: clean test docs ## Push to github
	git add .
	git commit -m "$m"
	git push

setup: clean test ## setup and build repo
	python setup.py sdist bdist_wheel bdist_egg
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
