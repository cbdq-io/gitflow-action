all: requirements lint

lint:
	yamllint -s .
	flake8

requirements:
	pip install -r .github/requirements/requirements.txt -r requirements-dev.txt
