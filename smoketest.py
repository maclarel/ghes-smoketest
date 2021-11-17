import argparse
import requests
import logging
import json
import pytest
from re import search

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
error_count = 0
request_count = 0


def validate_pat():
    if not ((len(pat) == 40) and (pat[0:4] == 'ghp_') and (pat[5:40].isalnum())):
        raise ValueError(
            'Pat is malformed.'
        )
            
def validate_target(target):
    # Ensure that URL is valid and well formed
    if not search('^htt(p|ps):/{2}.', target):
        raise ValueError(
            'Target URL must have an http[s]:// prefix and not be blank following it.')

def construct_api_url(endpoint):
    if endpoint == "status":
        return f"{target}/{endpoint}"
    return f"{target}/api/v3/{endpoint}"


def server_up():
    # Check that the server is up
    url = construct_api_url('status')
    response = requests.get(url, verify=False)
    logging.debug(f"Tested {url}, received response of {response.status_code}")
    if response.status_code == 200:
        logging.info(f"Server at {url} appears to be up!")
    else:
        raise Exception(
            'Server appears to be down or is not a GitHub Enterprise Server system. Please double check the URL.')


def get_pat_user(pat):
    # Ensure that we can auth with provided PAT, and return username if so
    url = construct_api_url('user')
    response = requests.get(url, headers=headers, verify=False)
    if 'Bad credentials' in response.text:
        logging.error(
            f"PAT authentication failed with error: {json.loads(response.text)['message']}")
        raise SystemExit
    logging.info(
        f"Running as {json.loads(response.text)['login']} - PAT auth confirmed working")
    return json.loads(response.text)['login']


def repo_list():
    # Create names of repositories to use
    return [f"smoketest_repo{num}" for num in range(1, num_repos+1)]


def api_call(endpoint, verb, expected_status, payload=None):
    # Test endpoint passed in to function and increment global counters
    logging.debug(
        f"Testing {verb} request for {endpoint}. Looking for {expected_status} response. Payload (if applicable): {payload}")
    url = construct_api_url(endpoint)
    if payload:
        response = requests.request(
            verb, url, headers=headers, data=json.dumps(payload), verify=False)
    else:
        response = requests.request(verb, url, headers=headers, verify=False)
    global request_count
    request_count += 1
    if response.status_code != expected_status:
        logging.error(
            f'{verb} request to {endpoint} failed! Expected a {expected_status} response, but got a {response.status_code} response.')
        global error_count
        error_count += 1
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
    headers = {'Accept': 'application/vnd.github.v3+json',
               'Authorization': 'token ' + pat}
    if args.num_repos:
        num_repos = args.num_repos

    try:
        validate_target(target)
    except ValueError as err:
        logging.error(f'Target URL validation failed with: {err}.')
        raise SystemExit

    try:
        server_up()
    except Exception as err:
        logging.error(err)
    else:
        username = get_pat_user(pat)
        for r in repo_list():
            start_err_count = error_count
            api_call('user/repos', 'post', 201, {'name': r})  # create a repo
            api_call(f'repos/{username}/{r}/issues', 'post', 201,
                     {'title': 'This is a test issue'})  # create an issue
            api_call(f'repos/{username}/{r}/contents/testfile', 'put', 201, {
                     'message': 'testfile', 'content': 'Zm9vCg=='})  # create a file with  content "foo"
<<<<<<< HEAD
            api_call(f'repos/{username}/{r}', 'delete', 204) # delete the repository
    else:
        logging.info(
            "Server appears to be down or is not a GitHub Enterprise Server system. Please double check the URL.")
=======
            # delete the repository
            api_call(f'repos/{username}/{r}', 'delete', 204)
            if error_count > start_err_count:
                logging.error(
                    f'Loop {r} completed with {error_count - start_err_count} errors.')
            else:
                logging.info(f'Loop {r} completed successfully.')
        if error_count:
            logging.error(
                f'Testing completed with {error_count} errors out of {request_count} API calls- {round(error_count/request_count * 100, 2)}% failure rate. Please review logs!')
        else:
            logging.info(f'Testing completed successfully.')
>>>>>>> refactor_1

# Tests
'''
this is the sane way to do this
    def test_repo():
        assert api_call('user/repos', 'get', 201, {'name': 'foo'}) is True
    
    def test_issue():
        assert api_call(f'repos/{username}/{r}/issues', 'post', 201, {'title': 'This is a test issue'}) is True

    def test_file():
        assert api_call(f'repos/{username}/{r}/contents/testfile', 'put',
                201, {'message': 'testfile', 'content': 'Zm9vCg=='}) is True

    def test_cleanup():
        assert api_call(f'repos/{username}/{r}', 'delete', 204) is True
'''

<<<<<<< HEAD
# let's try to dynamically generate this noise. 
# end goal is that we can add to the test suite by adding more hash table entries rather than hard coding the test.
class TestClass:
    testMaps = {'Test': {
                        'repo': {
                            'endpoint': 'user/repos',
                            'call': 'get',
                            'response': 201,
                            'options': {
                                'name': 'foo'
                            },
                            'assertResult':  True
                        },
                        'issues': {
                            'endpoint': f'repos/{username}/{r}/issues',
                            'call': 'get',
                            'response': 201,
                            'options': {
                                'title': 'This is a test issue'
                            },
                            'assertResult': True
                        },
                        'testfile': {
                            'endpoint': f'repos/{username}/{r}/contents/testfile',
                            'call': 'get',
                            'response': 201,
                            'options': {
                                'message': 'testfile', 
                                'content': 'Zm9vCg=='
                            },
                            'assertResult': True
                        },
                        'delRepo': {
                            'endpoint': f'repos/{username}/{r}',
                            'call': 'get',
                            'response': 204,
                            'options': {
                                'delete'
                            },
                            'assertResult': True
                        }
                    }
                }


    def testGen(endpoint, call, response, options, assertResult):
        def test(self):
            assert api_call(endpoint, call, response, options) is assertResult
        return test

    for params in testMaps.iteritems():
        test_func = testGen(params[0], params[1], params[2], params[3])
=======

def test_create():
    assert api_call('user/repos', 'get', 201, {'name': 'foo'}) is True


def test_issues():
    assert api_call(f'repos/{username}/{r}/issues', 'post',
                    201, {'title': 'This is a test issue'}) is True


def test_file():
    assert api_call(f'repos/{username}/{r}/contents/testfile', 'put',
                    201, {'message': 'testfile', 'content': 'Zm9vCg=='}) is True


def test_delete():
    assert api_call(f'repos/{username}/{r}', 'delete', 204) is True
>>>>>>> refactor_1
