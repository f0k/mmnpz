.PHONY: tests build format docs

tests:
	isort --check .
	black --check .
	ruff check .
	mypy .
	pytest .

build:
	rm -rf *.egg-info/
	python3 -m build

format:
	isort .
	black .

docs:
	rm -rf docs/build/
	sphinx-autobuild -b html --watch src/ --watch .github/CONTRIBUTING.md --watch CHANGELOG.md docs/source/ docs/build/
