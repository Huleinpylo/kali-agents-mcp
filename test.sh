#!/bin/bash
# This script runs the tests using pytest.
# It creates/activates a virtual environment and installs dependencies.

set -e

if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

export PYTHONPATH=$PWD
pytest
