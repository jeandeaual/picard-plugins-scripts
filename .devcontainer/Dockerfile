# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.217.1/containers/python-3/.devcontainer/base.Dockerfile

ARG VARIANT="3.6-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# hadolint ignore=DL3008
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Required to build python-picard
    gettext \
    # Required by PyQt5
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER vscode

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.1.13 python -

# Install prettier
RUN npm install -g prettier@2.5.1
