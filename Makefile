all: requirements lint build test

build:
	docker buildx build --load -t gitflow:latest .

lint:
	yamllint -s .
	flake8
	docker run --rm -i hadolint/hadolint < Dockerfile

requirements:
	pip install -r .github/requirements/requirements.txt -r requirements-dev.txt

test:
	docker run --rm -e ACTIONS_STEP_DEBUG=true -v '.:/mnt/src' -w /mnt/src gitflow:latest main develop feature/ bugfix/ release/ hotfix/ support/ 'v' 0.1.0
