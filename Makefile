all: requirements lint

lint:
	yamllint -s .
	flake8
	docker run --rm -i hadolint/hadolint < Dockerfile

requirements:
	pip install -r .github/requirements/requirements.txt -r requirements-dev.txt
