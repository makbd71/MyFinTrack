#!/usr/bin/env bash
# One-time local setup: virtualenv, dependencies, .env, tests.
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

if [ ! -f .env ]; then
  cp .env.example .env
  chmod 600 .env
  echo "Created .env — open it and fill in MAIL_ADDRESS, MAIL_APP_PASSWORD and REPORT_RECIPIENT."
fi

mkdir -p data output logs .tmp
.venv/bin/python -m pytest
echo "Setup complete. Activate with: source .venv/bin/activate"
