#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Create virtual environment on first run
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

pip install -q -r requirements.txt

# Make sure .env exists
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add your API keys, then re-run."
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: ./run.sh --query \"your research question\""
  exit 1
fi

python -m app.main "$@"