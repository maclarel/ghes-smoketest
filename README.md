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

Successful run:

```
$ python3 smoketest.py -p <pat> -t https://fakeserver.net -n 2
2021-11-16 18:58:48,253 INFO: Server at https://fakeserver.net/status appears to be up!
2021-11-16 18:58:48,444 INFO: Running as user1 - PAT auth confirmed working
2021-11-16 18:58:50,636 INFO: Loop smoketest_repo1 completed successfully.
2021-11-16 18:58:52,470 INFO: Loop smoketest_repo2 completed successfully.
2021-11-16 18:58:52,470 INFO: Testing completed successfully.
```

Failing run:

```
$ python3 smoketest.py -p <pat> -t https://fakeserver.net -n 2
2021-11-17 08:25:25,168 INFO: Server at https://fakeserver.net/status appears to be up!
2021-11-17 08:25:25,369 INFO: Running as user1 - PAT auth confirmed working
2021-11-17 08:25:25,755 ERROR: post request to user/repos failed! Expected a 201 response, but got a 422 response.
2021-11-17 08:25:26,423 ERROR: put request to repos/user1/smoketest_repo1/contents/testfile failed! Expected a 201 response, but got a 422 response.
2021-11-17 08:25:26,683 ERROR: Loop smoketest_repo1 completed with 2 errors.
2021-11-17 08:25:26,888 ERROR: post request to user/repos failed! Expected a 201 response, but got a 422 response.
2021-11-17 08:25:27,567 ERROR: put request to repos/user1/smoketest_repo2/contents/testfile failed! Expected a 201 response, but got a 422 response.
2021-11-17 08:25:27,842 ERROR: Loop smoketest_repo2 completed with 2 errors.
2021-11-17 08:25:27,842 ERROR: Testing completed with 4 errors - 50.0% failure rate. Please review logs!
```

Bad PAT:

```
$ python3 smoketest.py -p <bad_pat> -t https://fakeserver.net -n 2
2021-11-17 08:36:05,389 INFO: Server at https://fakeserver.net/status appears to be up!
2021-11-17 08:36:06,206 ERROR: PAT authentication failed with error: Bad credentials. Please check credentials.
```

## FAQ

> We have rate limiting enabled. How many API calls does this make?

This script will make 42 API calls by default. 41 of these are subject to the rate limit, and 1 is not (the call to `/status` to ensure that the server is operational). Effectively, the number of calls will be equal to `(<num value> * # of tests)+2`.

> It seems like some of this could be done more efficiently via GraphQL rather than the REST API. Why not use it?

The goal of this is not efficiency, but _coverage_. A single GraphQL call to do a significant amount of work only gives us a binary failure state. If we can spread that, instead, across tens/hundreds of API calls we'll get a better idea of how reliably GitHub Enterprise Server is able to respond. This is especially important for deployments that have a load balancer appliance sitting in front of GitHub Enterprise Server as we're more likely to hit many/all of the underlying servers in this test.

> I'm getting spammed with `InsecureRequestWarning` messages when I run this. What's up?

You're probably using a self-signed certificate. I've already added `verify=False` to all of the API calls that are being done in this script to try to work around this in most cases, however you'll still get these annoying errors.

The *best* solution is to ensure you've got the CA for server added to your local system, however barring that you could run `export PYTHONWARNINGS="ignore:Unverified HTTPS request"` to disable this warning.

Obviously I'd prefer that you use a valid cert, but I know that's not always realistic.

> Why Python and not Ruby?

I felt like working on a project in Python. 🤷

> Can you add testing for X endpoint?

Sure - please feel free to fork and open a Pull Request! Fortunately, with `requests` in Python it's pretty trivial to add new functionality here, so I'd encourage it as a learning project for anyone interested. This should be as simple as adding a new `api_call()` invocation with the proper arguments.
