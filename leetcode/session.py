from typing import Dict, Optional
import logging

from leetcode.exception import LeetCodeOperationFailureError
from leetcode.third_party import requests
from leetcode.urls import BASE_URL

log = logging.getLogger(__name__)

_session = requests.Session()


LOGIN_URL = 'https://leetcode.com/accounts/login/'


def _make_headers() -> Dict[str, str]:
    headers = {'Origin': BASE_URL,
               'Referer': BASE_URL,
               'X-CSRFToken': _session.cookies['csrftoken'],
               'X-Requested-With': 'XMLHttpRequest'}

    return headers


def post(url, headers: Optional[dict] = None, json: Optional[dict] = None,
         data: Optional[dict] = None, **kwargs) -> requests.Response:

    post_headers = _make_headers()

    if headers:
        post_headers.update(headers)

    log.info('POST request: url=%s headers=%s', url, post_headers)
    log.debug('POST request body: %s %s', data, json)

    response = _session.post(url, headers=post_headers, data=data, json=json,
                             **kwargs)

    log.info('POST response: %s', response.status_code)
    log.debug('POST response body: %s', response.text)

    return response


def get(url, headers: Optional[dict] = None, **kwargs) -> requests.Response:
    get_headers = _make_headers()

    if headers:
        get_headers.update(headers)

    log.info('GET request: url=%s headers=%s', url, get_headers)

    response = _session.get(url, headers=get_headers, **kwargs)

    log.info('GET response: %s', response.status_code)
    log.debug('GET response body: %s', response.text)

    return response


def login(username: str, password: str) -> None:
    res = _session.get(LOGIN_URL)

    if res.status_code != 200:
        log.error('login failed: %s', res.reason)
        raise LeetCodeOperationFailureError('Could not get login page')

    headers = {'Origin': BASE_URL,
               'Referer': LOGIN_URL}

    form = {'csrfmiddlewaretoken': _session.cookies['csrftoken'],
            'login': username,
            'password': password}

    log.info('login request: POST %s headers=%s username=%s', LOGIN_URL,
             headers, username)

    # requests follows the redirect url by default
    # disable redirection explicitly
    res = _session.post(
        LOGIN_URL,
        data=form,
        headers=headers,
        allow_redirects=False)

    log.info('login response: status=%s', res.status_code)
    log.debug('login response body: %s', res.text)

    if res.status_code != 302:
        raise LeetCodeOperationFailureError('Username or password not correct')
