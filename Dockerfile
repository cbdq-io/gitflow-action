FROM python:3.12-alpine

COPY .github/scripts/git_flow.py /git_flow.py
COPY .github/requirements/requirements.txt /requirements.txt

# hadolint ignore=DL3018
RUN apk add --no-cache git \
  && pip install --no-cache-dir --quiet -r /requirements.txt

ENTRYPOINT [ "python", "/git_flow.py" ]
