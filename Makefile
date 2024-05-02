all: requirements lint

lint:
	yamllint -s .

requirements:
	pip install -r requirements-dev.txt
