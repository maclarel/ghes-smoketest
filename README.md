# GHES Smoke Test

This is a Python script that will hit various API endpoints (in moderate volumes) using a provided PAT and report on success/failure rates.  The tool will clean up after itself, deleting any repositories/issues/files/etc... created during testing.

This tool will specifically test functionality using _newly created repositories_. It is not intended to advise on the health of any existing repositories, and should not be used as the only source of truth for validating functionality of GitHub Enterprise Server.

## Requirements

- Python 3
- `requests` module (`$ python -m pip install requests`)
- Supplied PAT must have `delete_repo, repo` scopes

## Usage

```
smoketest.py [-p] -pat PERSONAL_ACCESS_TOKEN [-t] -target GHES_URL [-n] -num NUM_REPOS [-debug]

Performs simple testing against GitHub Enterprise Server to ensure basic functionality. By default, each endpoint will be tested 10 times.

Required arguments:
    -p, -pat    The personal access token to use for access
    -t, -target   The URL of the target GitHub Enterprise Server instance (e.g. https://github.company.com)

Optional arguments:
    -debug      Display response output as JSON
    -n, -num    Number of repositories to create during testing (default 10)
```

## Example output

```
$ python3 smoketest.py -p <pat_for_user1_goes_here> -t https://github.fakecompany.net -n 2
2021-11-11 12:39:50,966 INFO: Server at https://github.fakecompany.net/status appears to be up!
2021-11-11 12:39:51,437 INFO: Running as user1 - PAT auth confirmed working
2021-11-11 12:39:51,437 INFO: Testing creation of smoketest repositories
2021-11-11 12:39:53,423 INFO: Repostiory creation returned 0 errors out of 2 attempts. 0.0% failure rate.
2021-11-11 12:39:53,424 INFO: Testing creation of Issues in smoketest repositories
2021-11-11 12:39:54,670 INFO: Issue creation returned 0 errors out of 2 attempts. 0.0% failure rate.
2021-11-11 12:39:54,670 INFO: Testing file creation in each smoketest repository
2021-11-11 12:39:55,654 INFO: File creation returned 0 errors out of 2 attempts. 0.0% failure rate.
2021-11-11 12:39:55,654 INFO: Testing deletion of smoketest repositories
2021-11-11 12:39:56,463 INFO: Repository deletion returned 0 errors out of 2 attempts. 0.0% failure rate.
```
