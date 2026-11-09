all: requirements lint build test

build:
	docker buildx build --load -t gitflow:latest .

changelog:
	docker run --platform linux/amd64 --quiet --rm --volume "${PWD}:/mnt/source" --workdir /mnt/source ghcr.io/cbdq-io/gitchangelog > CHANGELOG.md

lint:
	yamllint -s .
	ruff format
	ruff check --fix .
	bandit -qr .
	docker run --rm -i hadolint/hadolint < Dockerfile

requirements:
	pip install -r .github/requirements/requirements.txt -r requirements-dev.txt

test:
	docker run --rm -e ACTIONS_RUNNER_DEBUG=true -v '.:/mnt/src' -w /mnt/src gitflow:latest main develop feature/ bugfix/ release/ hotfix/ support/ 'v' 0.1.0
