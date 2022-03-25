.PHONY: clean help lint test docs nixenv
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
import os, shutil
from pathlib import Path
from torrentfile.version import __version__ as version
for item in Path("./dist").iterdir():
	if item.is_dir() and item.name == "torrentfile_linux":
		name = f"TorrentFile{version}-linux"
		path = item.parent / name
		shutil.move(item, path)
		shutil.make_archive(path, 'zip', path)
	elif item.is_dir() and item.name == 'torrentfile':
		name = f"TorrentFile{version}-win"
		path = item.parent / name
		shutil.move(item, path)
		shutil.make_archive(path, 'zip', path)
	elif item.is_file() and item.name == "torrentfile":
		name = f"torrentfile{version}-linux"
		os.rename(item, item.parent / name)
	elif item.suffix == ".exe":
		newname = f"{item.stem}{version}.exe"
		full = item.parent / newname
		os.rename(item, full)
endef
export FIX_BIN_VERSION_FILES

define UPDATE_PACKAGE_VERSION
import json
from torrentfile.version import __version__
data = json.load(open("package.json"))
if data['version'] != __version__:
	data['version'] = __version__
	json.dump(data, open("package.json", "wt"), indent=2)
endef
export UPDATE_PACKAGE_VERSION

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@echo Cleaning
	rm -rf build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .tox/
	rm -fv .coverage
	rm -fv coverage.xml
	rm -fr htmlcov/
	rm -fv corbertura.xml
	rm -fr .pytest_cache
	rm -rf Release
	rm -rf node_modules
	rm -f torrentfile.log
	rm -f -- *'.spec'
	rm -fr -- *'/__pycache__'


test: ## Get coverage report
	python setup.py install
	pytest --cov=torrentfile --cov=tests

lint:
	black torrentfile tests
	isort torrentfile tests
	prospector torrentfile
	prospector tests

docs: ## Regenerate docs from changes
	python -c "$$UPDATE_PACKAGE_VERSION"
	rm -rfv docs/*
	rm -rfv site/index.md
	cp -rfv README.md site/index.md
	cp -rfv CHANGELOG.md site/changelog.md
	mkdocs build
	touch docs/.nojekyll

coverage: ## Get coverage report
	coverage run -m pytest
	coverage xml
	bash coverage.sh report -r coverage.xml

push: clean lint docs test coverage ## Push to github
	git add .
	git commit -m "$m"
	git push

setup: clean test lint docs ## setup and build repo
	pip install --pre --upgrade --force-reinstall --no-cache -rrequirements.txt
	python setup.py sdist bdist_wheel bdist_egg
	pip install -e .
	twine upload dist/*

build: clean test lint docs
	pip install --pre --upgrade --force-reinstall --no-cache -rrequirements.txt
	pip install pyinstaller
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

nixenv: ## activate unix python vurtual environment
	source nixenv/bin/activate

nixbuild:
	pip install pyinstaller
	python3 setup.py sdist bdist_wheel bdist_egg
	pip install -e .
	rm -rfv ../runner
	mkdir ../runner
	touch ../runner/exec
	cp ./assets/favicon.png ../runner/favicon.png
	@echo "import torrentfile" >> ../runner/exec
	@echo "torrentfile.main()" >> ../runner/exec
	pyinstaller --distpath ../runner/dist --workpath ../runner/build \
		-F -n torrentfile -c -i ../runner/favicon.png \
		--specpath ../runner/ ../runner/exec
	pyinstaller --distpath ../runner/dist --workpath ../runner/build \
		-D -n torrentfile_linux -c -i ../runner/favicon.png \
		--specpath ../runner/ ../runner/exec
	cp -rfv ../runner/dist/* ./dist/
	python3 -c "$$FIX_BIN_VERSION_FILES"
