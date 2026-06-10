all: requirements lint build test

build:
	docker buildx build --load -t gitflow:latest .

changelog:
	docker run --platform linux/amd64 --quiet --rm --volume "${PWD}:/mnt/source" --workdir /mnt/source ghcr.io/cbdq-io/gitchangelog > CHANGELOG.md

lint:
	yamllint -s .
	isort -v .
	flake8
	docker run --rm -i hadolint/hadolint < Dockerfile

requirements:
	pip install -r .github/requirements/requirements.txt -r requirements-dev.txt

test:
	docker run --rm -e ACTIONS_RUNNER_DEBUG=true -v '.:/mnt/src' -w /mnt/src gitflow:latest main develop feature/ bugfix/ release/ hotfix/ support/ 'v' 0.1.0

update-requirements:
	pip freeze > /tmp/requirements-all.txt
	docker run --entrypoint pip --rm gitflow:latest freeze > .github/requirements/requirements.txt
	comm -23 /tmp/requirements-all.txt .github/requirements/requirements.txt > requirements-dev.txt
