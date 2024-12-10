FROM python:3.12

RUN apt update && apt install -y python3-pip python3-dev default-libmysqlclient-dev build-essential pkg-config

COPY pyproject.toml /wikiagents/pyproject.toml
WORKDIR /wikiagents

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1
ENV PATH="$PATH:$POETRY_HOME/bin"
RUN pip3 install poetry
RUN poetry install
COPY api /wikiagents/api
WORKDIR /wikiagents
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]