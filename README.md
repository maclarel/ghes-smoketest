# GHES Smoke Test

This is a Python script that will hit various API endpoints (in moderate volumes) using a provided PAT and report on success/failure rates.  The tool will clean up after itself, deleting any repositories/issues/etc... created during testing.

Note: This tool will specifically test functionality using _newly created_ repositories. It is not intended to advise on the health of any other repositories, and should not be used as the only source of truth for validating functionality of GitHub Enterprise Server.

## Requirements

- python3
- requests module ($ python -m pip install requests)

## Usage

python3 smoketest.py [-p] -pat PERSONAL_ACCESS_TOKEN [-h] -target GHES_URL [-debug]

Performs simple testing against GitHub Enterprise Server to ensure basic functionality. By default, each endpoint will be tested 10 times.

Required arguments:
    -p, -pat    The personal access token to use for access
    -t, -target   The URL of the target GitHub Enterprise Server instance (e.g. https://github.company.com)

Optional arguments:
    -debug      Display response output as JSON

