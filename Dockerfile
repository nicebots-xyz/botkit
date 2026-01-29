# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20
FROM python:${PYTHON_VERSION}-slim-bookworm AS python-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

WORKDIR /app
COPY src pyproject.toml pdm.lock ./

RUN pdm export --prod -o requirements.txt

FROM python:${PYTHON_VERSION}-slim-bookworm AS app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser -u 6392 --disabled-password --gecos "" appuser && chown -R appuser /app

COPY --from=python-base --chown=appuser /app/requirements.txt ./

RUN pip install -r requirements.txt

COPY --chown=appuser src/ ./src
COPY --chown=appuser LICENSE ./

USER appuser

CMD ["python", "src"]
