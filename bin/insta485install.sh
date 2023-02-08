#!/bin/bash
#insta485install

set -Eeuo pipefail
set -x

# Virtual environment setup
python3 -m venv env
source env/bin/activate

# Install back end
pip install -r requirements.txt
pip install -e .

# Intall front end
npm ci .
