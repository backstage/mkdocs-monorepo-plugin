#!/bin/bash

# Lint via flake8
echo "Running flake8 linter -------->"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=setup.py
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=setup.py

# Running unit-tests
python3 -m unittest

# End-to-end testing via Bats (Bash automated tests)
function docker_run_integration_tests() {
docker build -t mkdocs-monorepo-test-runner:$1 --quiet -f- . <<EOF
  FROM python:$1
  COPY ./requirements.txt /workspace/requirements.txt
  RUN apt-get -y update && apt-get -yyy install bats && apt-get -yyy install git
  RUN pip install -r /workspace/requirements.txt
  ENTRYPOINT ["bats"]
  CMD ["/workspace/__tests__/integration/test.bats"]
EOF

echo "Running E2E tests via Bats in Docker (python:$1) -------->"
docker run -it -w /workspace -v $(pwd):/workspace mkdocs-monorepo-test-runner:$1
}

if [[ ! -z "$PYTHON_37_ONLY" ]]; then
  docker_run_integration_tests "3.7-slim"
else
  docker_run_integration_tests "3-slim"
  docker_run_integration_tests "3.7-slim"
  docker_run_integration_tests "3.8-slim"
  docker_run_integration_tests "3.9-slim"
  docker_run_integration_tests "3.10-slim"
  docker_run_integration_tests "3.11-slim"
fi
