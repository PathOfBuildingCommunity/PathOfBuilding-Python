.DEFAULT_GOAL := all
isort = isort -m 3 pob
black = black -l 88 --target-version py39 pob


.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: build
build:
	@echo "no build defined yet"
#	python setup.py build_ext --inplace


.PHONY: format
format:
	$(isort)
	$(black)


.PHONY: lint
lint:
	$(isort) --check-only --df
	$(black) --check --diff


.PHONY: mypy
mypy:
	mypy pob


.PHONY: test
test:
	@echo "tests undefined"
#	pytest --cov=pob


.PHONY: all
all: lint mypy test


.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
#	python setup.py clean
