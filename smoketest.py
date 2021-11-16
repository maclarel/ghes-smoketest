import argparse
import requests
import logging
import json
import pytest

'''
Usage: smoketest.py [-p] -pat PERSONAL_ACCESS_TOKEN [-t] -target GHES_URL [-n] -num NUM_REPOS [-debug]

Performs simple testing against GitHub Enterprise Server to ensure basic functionality. By default, each endpoint will be tested 10 times.

Required arguments:
    -p, -pat    The personal access token to use for access
    -t, -target   The URL of the target GitHub Enterprise Server instance (e.g. https://github.company.com)

Optional arguments:
    -debug      Display response output as JSON
    -n, -num    Number of repositories to create during testing (default 10)
'''

pat = ""
target = ""
num_repos = 10
headers = {'Accept': 'application/vnd.github.v3+json',
           'Authorization': 'token ' + pat}


def validate_args():
    # Ensure that URL is valid and PAT is well formed
    # TO DO
    pass


def construct_api_url(endpoint):
    if endpoint == "status":
        return f"{target}/{endpoint}"
    return f"{target}/api/v3/{endpoint}"


def server_up():
    url = construct_api_url('status')
    response = requests.get(url, verify=False)
    logging.debug(f"Tested {url}, received response of {response.status_code}")
    if response.status_code == 200:
        logging.info(f"Server at {url} appears to be up!")
        return True


def get_pat_user(pat):
    url = construct_api_url('user')
    response = requests.get(url, headers=headers, verify=False)
    return json.loads(response.text)['login']


def repo_list():
    # Create names of repositories to use
    return [f"smoketest_repo{num}" for num in range(1, num_repos+1)]


def api_call(endpoint, verb, expected_status, payload=None):
    # Test endpoint passed in to function
    logging.debug(
        f"Testing {verb} request for {endpoint}. Looking for {expected_status} response. Payload (if applicable: {payload}")
    url = construct_api_url(endpoint)
    if payload:
        response = requests.request(
            verb, url, headers=headers, data=json.dumps(payload), verify=False)
    else:
        response = requests.request(verb, url, headers=headers, verify=False)
    if response.status_code != expected_status:
        logging.error(
            f'{verb} request to {endpoint} failed! Expected a {expected_status} response, but got a {response.status_code} response.')
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Performs API & Git smoketests against GitHub Enterprise Server')
    parser.add_argument('-target', dest='target', type=str,
                        help='The URL of the GHES instance, e.g. https://github.foo.com', required=True)
    parser.add_argument('-pat', dest='pat', type=str,
                        help='Personal Access Token to use for access', required=True)
    parser.add_argument('-num', dest='num_repos', type=int,
                        help='Number of repostiories to create (default 10)', required=False)
    parser.add_argument('-debug', dest='debug', action='store_true',
                        help='Display response JSON', required=False)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    target = args.target
    pat = args.pat
    if args.num_repos:
        num_repos = args.num_repos
    headers = {'Accept': 'application/vnd.github.v3+json',
               'Authorization': 'token ' + pat}

    if server_up():
        logging.info(
            f"Running as {get_pat_user(pat)} - PAT auth confirmed working")
        username = get_pat_user(pat)
        for r in repo_list():
            api_call('user/repos', 'post', 201, {'name': r}) # create a repo
            api_call(f'repos/{username}/{r}/issues', 'post', 201,
                     {'title': 'This is a test issue'})  # create an issue
            api_call(f'repos/{username}/{r}/contents/testfile', 'put', 201, {
                     'message': 'testfile', 'content': 'Zm9vCg=='})  # create a file with  content "foo"
            api_call(f'repos/{username}/{r}', 'delete', 204) # delete the repository
    else:
        logging.info(
            "Server appears to be down or is not a GitHub Enterprise Server system. Please double check the URL.")


# Tests

def test_loop():
    assert api_call('user/repos', 'get', 201, {'name': 'foo'}) is True
    #assert api_call('user/repos', 'post', 201, {'name':'foo'}) is False
    assert api_call(f'repos/{username}/{r}/issues', 'post',
                    201, {'title': 'This is a test issue'}) is True
    assert api_call(f'repos/{username}/{r}/contents/testfile', 'put',
                    201, {'message': 'testfile', 'content': 'Zm9vCg=='}) is True
    assert api_call(f'repos/{username}/{r}', 'delete', 204) is True
