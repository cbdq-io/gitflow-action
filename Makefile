all: requirements lint

lint:
	yamllint -s .
	flake8

requirements:
	pip install -r requirements-dev.txt
