.PHONY: clean help lint test docs nixenv
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
import shutil
from torrentfile.version import __version__
shutil.copy("./dist/temp.zip", "./dist/torrentfile-v" + __version__ + "-win.zip")
endef
export RENAME_FILE

BROWSER := python -c "$$BROWSER_PYSCRIPT"

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
	rm -fv -- *'.spec'
	rm -fvr -- *'/__pycache__'
	rm -frv runner/build
	rm -frv runner/dist

test: ## Get coverage report
	tox

docs: ## Regenerate docs from changes
	python -c "$$UPDATE_PACKAGE_VERSION"
	rm -rfv docs/*
	rm -rfv site/index.md
	cp -rfv README.md site/index.md
	cp -rfv CHANGELOG.md site/changelog.md
	mkdocs build
	touch docs/.nojekyll

push: clean docs test ## Push to github
	git add .
	git commit -m "$m"
	git push

setup: clean test lint ## setup and build repo
	pip install --pre --upgrade --force-reinstall --no-cache -rrequirements.txt
	python setup.py sdist bdist_wheel bdist_egg
	pip install -e .
	twine upload dist/*

release: clean test lint ## create executables for release
	pip install pyinstaller
	pip install -e .
	pyinstaller ./runner/execf.spec
	mkdir ./dist/temp
	cp ./dist/torrentfile.exe ./dist/temp/
	7z a ./dist/temp.zip ./dist/temp
	python -c $$RENAME_FILE
