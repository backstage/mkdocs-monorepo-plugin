#!/bin/bash

# Lint via flake8
echo "Running flake8 linter -------->"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=setup.py
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=setup.py

# Running unit-tests
python3 -m unittest

# End-to-end testing via Bats (Bash automated tests)
GITHUB_ACTIONS_E2E_PATH="/home/runner/work/mkdocs-monorepo-plugin/mkdocs-monorepo-plugin/__tests__/integration/test.bats"
LOCAL_E2E_PATH="./integration/test.bats"

if [[ -f "$GITHUB_ACTIONS_E2E_PATH" ]]; then
    bats $GITHUB_ACTIONS_E2E_PATH
elif [[ -f "$LOCAL_E2E_PATH" ]]; then
    bats $LOCAL_E2E_PATH
else
    echo "Could not find the test.bats file. Please check /__tests__/test-ci.sh and correct the paths."
    exit 1
fi

