import argparse
import requests
import logging
import json

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


def test_repo_creation():
    # Test creation of repositories
    logging.info("Testing creation of smoketest repositories")
    logging.debug(f"Creating the following repositories: {repo_list()}")
    url = construct_api_url('user/repos')
    error_count = 0
    for r in repo_list():
        payload = {
            'name': r
        }
        response = requests.post(url, headers=headers,
                                 data=json.dumps(payload), verify=False)
        # We expect a 201 response for confirmed repo creation
        if response.status_code != 201:
            error_count += 1
    logging.info(f"Repostiory creation returned {error_count} errors")


def test_repo_deletion():
    # Delete repositories created in test_repo_creation
    logging.info("Testing deletion of smoketest repositories")
    logging.debug("Deleting the following repsitories: {repo_list()}")
    username = get_pat_user(pat)
    error_count = 0
    for r in repo_list():
        url = construct_api_url('repos/' + username + '/' + r)
        response = requests.delete(url, headers=headers, verify=False)
        # We expect a 204 response on positive deletion
        if response.status_code != 204:
            error_count += 1
    logging.info(f"Repository deletion returned {error_count} errors")


def test_issues():
    # Creates an issue in each smoketest repository, then deletes it.
    logging.info("Testing creation of Issues in smoketest repositories")
    logging.debug(
        f"Creating an Issue in each of the following repostiories: {repo_list()}")
    username = get_pat_user(pat)
    error_count = 0
    payload = {
        'title': 'This is a test issue'
    }
    for r in repo_list():
        url = construct_api_url('repos/' + username + '/' + r + '/issues')
        response = requests.post(url, headers=headers,
                                 data=json.dumps(payload), verify=False)
        # We expect a 201 response on positive deletion
        if response.status_code != 201:
            error_count += 1
    logging.info(f"Issue creation returned {error_count} errors")


def test_file_creation():
    # Creates a file in each smoketest repository
    logging.info("Testing file creation in each smoketest repository")
    logging.debug(
        f"Creating a single file in each of the following repositories: {repo_list()}")
    username = get_pat_user(pat)
    error_count = 0
    payload = {
        "message": "message",
        "content": "Zm9vCg=="  # 'foo'
    }
    for r in repo_list():
        url = construct_api_url('repos/' + username +
                                '/' + r + '/contents/testfile')
        response = requests.put(url, headers=headers,
                                data=json.dumps(payload), verify=False)
        # We expect a 201 response on positive file creation
        if response.status_code != 201:
            error_count += 1
    logging.info(f"File creation returned {error_count} errors")


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
        test_repo_creation()
        # test_issues()
        # test_file_creation()
        test_repo_deletion()
    else:
        logging.info(
            "Server appears to be down or is not a GitHub Enterprise Server system. Please double check the URL.")
