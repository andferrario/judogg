#!/bin/sh
# Serial on purpose: the ingestion tests rewrite the app tables, then the app tests read the loaded fixtures.
set -eu
export DATABASE_URL="$TEST_DATABASE_URL"
alembic upgrade head
rm -f .coverage
pytest tests/test_text.py tests/db tests/ingestion --cov=judogg --cov-report=
judogg-ingest load --files tests/fixtures/ijf
pytest tests/app --cov=judogg --cov-append --cov-report=
echo "Domain coverage (gate: 100%)"
coverage report --include='src/judogg/*/domain/*' --fail-under=100
echo "Overall coverage (reported only)"
coverage report
