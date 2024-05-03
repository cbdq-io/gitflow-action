FROM python:3.12

COPY .github/scripts/git_flow.py /git_flow.py
COPY .github/requirements/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT [ "python", "/git_flow.py" ]
