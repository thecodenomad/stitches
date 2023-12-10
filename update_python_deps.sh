#!/bin/bash

#
# Make sure to add `flatpak-pip-generator` to your path (usually $HOME/.local/bin)
#

set -e

# Make sure poetry handles the environment, to keep things contained
# it might be better setting in-project to true:
# `poetry config virtualenvs.in-project true`

# Setup the environment if it doesn't exist
poetry install --no-root

# Generate the requirements.txt file
poetry export --without-hashes --format=requirements.txt > requirements.txt

# Activate the environment
source .venv/bin/activate
flatpak-pip-generator --requirements-file=requirements.txt --output python-deps
deactivate
