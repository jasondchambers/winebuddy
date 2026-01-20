# Vulnerability management

To scan for packages with known vulnerabilities, pip-audit should be run as
follows:

    uvx pip-audit

If vulnerabilities are discovered, dependencies can be updates using uv as
follows:

    uv sync --upgrade-package <package-name>

All tests must be run to ensure it still works - see the "Testing and development"
section below.

# Code quality 

For the Python code, [Ruff](https://github.com/astral-sh/ruff) is used:

    uvx ruff check   # Lint all files in the current directory.

For checking types in the Python code, [pyright](https://github.com/microsoft/pyright) is used:

    uvx pyright .

For the shell scripts, [shellcheck](https://github.com/koalaman/shellcheck) is
used:

    shellcheck *.sh

# Security scanning

For the Python code, [Bandit](https://github.com/astral-sh/ruff) is used:

    uvx bandit -c bandit.yaml *.py

# Formatting

For the Python code, [Ruff](https://github.com/astral-sh/ruff) is used:

    uvx ruff format  # Format all files in the current directory.

# Testing and development

There are CLI tests available that verify the observable behavior of winebuddy
by comparing the output of test runs with expected output. The tests can be run
as follows:

    ./test.sh

This makes it ideal to incorporate into a CI/CD pipeline.

Check the $? variable - if 0, all tests have passed.

