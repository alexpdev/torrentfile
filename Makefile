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
import shutil
import sys
import subprocess
import time
from torrentfile.version import __version__
if sys.platform == "win32":
	time.sleep(2)
	subprocess.Popen(["7z", "a", "./dist/temp.zip", "./dist/torrentfile.exe"])
	time.sleep(2)
	shutil.copy(
		"./dist/temp.zip",
		"./dist/torrentfile-v" + __version__ + "-win.zip")
else:
	time.sleep(2)
	subprocess.Popen(["zip", "./dist/temp.zip", "./dist/torrentfile"])
	time.sleep(2)
	shutil.copy(
		"./dist/temp.zip",
		"./dist/torrentfile-v" + __version__ + "-linux.zip")
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

extra: ## extra imports
	pip install torrentfile torrentfileQt QStyler ebookatty --force-reinstall --no-cache --upgrade

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
	pip install --pre --upgrade --force-reinstall --no-cache -rrequirements.txt
	python setup.py sdist bdist_wheel bdist_egg
	pip install -e .
	twine upload dist/*

release: clean test ## create executables for release
	pip install pyinstaller
	pip install -e .
	pyinstaller ./runner/execf.spec
	@python -c "$$RENAME_FILE"
