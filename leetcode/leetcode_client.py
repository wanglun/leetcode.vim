from datetime import datetime
import json
import logging
from pprint import pformat
import re
from typing import List, Any, Union

from leetcode import urls, graphql_queries
from leetcode import messages
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.types import Problem, ProblemState, Difficulty, ProblemDetail, \
    Submission, SubmissionDetail, TestJob, SubmissionRequest, TestResult, \
    RunningSubmission, SubmissionResult
from leetcode.third_party import requests


log = logging.getLogger(__name__)


_session = requests.Session()


def _check_login():
    if _session is None:
        raise LeetCodeOperationFailureError(messages.NOT_LOGGED_IN)


def _make_headers():
    assert _session is not None

    headers = {'Origin': urls.BASE_URL,
               'Referer': urls.BASE_URL,
               'X-CSRFToken': _session.cookies['csrftoken'],
               'X-Requested-With': 'XMLHttpRequest'}

    return headers


def login(username: str, password: str) -> None:
    global _session

    log.info('login init request: GET %s', urls.LOGIN_URL)
    res = _session.get(urls.LOGIN_URL)
    log.info('login init response: status=%s', res.status_code)

    if res.status_code != 200:
        log.error('login failed: %s', res.reason)
        raise LeetCodeOperationFailureError(messages.GET_LOGIN_PAGE_FAILURE)

    headers = {'Origin': urls.BASE_URL,
               'Referer': urls.LOGIN_URL}

    form = {'csrfmiddlewaretoken': _session.cookies['csrftoken'],
            'login': username,
            'password': password}

    log.info('login request: POST %s headers=%s username=%s', urls.LOGIN_URL,
             headers, username)

    # requests follows the redirect url by default
    # disable redirection explicitly
    res = _session.post(
        urls.LOGIN_URL,
        data=form,
        headers=headers,
        allow_redirects=False)

    log.info('login response: status=%s', res.status_code)
    log.debug('login response body: %s', res.text)

    if res.status_code != 302:
        raise LeetCodeOperationFailureError(messages.LOGIN_FAILURE)


def _from_api_state(state: str) -> ProblemState:
    if state == 'ac':
        return ProblemState.AC
    if state == 'notac':
        return ProblemState.NOT_AC
    return ProblemState.NEW


def _from_api_difficulty(level: str) -> Difficulty:
    if level == 1:
        return Difficulty.EASY
    if level == 2:
        return Difficulty.MEDIUM
    if level == 3:
        return Difficulty.HARD
    return Difficulty.UNKNOWN


def _from_api_text_difficulty(difficulty: str) -> Difficulty:
    if difficulty == 'Easy':
        return Difficulty.EASY
    if difficulty == 'Medium':
        return Difficulty.MEDIUM
    if difficulty == 'Hard':
        return Difficulty.HARD
    return Difficulty.UNKNOWN


def get_problem_list() -> List[Problem]:
    _check_login()

    headers = _make_headers()
    url = urls.PROBLEM_LIST_URL

    log.info('get_problem_list request: GET %s headers=%s', url, headers)

    res = _session.get(url, headers=headers)

    log.info('get_problem_list response: status=%s', res.status_code)
    log.debug('get_problem_list response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(messages.GET_PROBLEM_LIST_FAILURE)

    problem_list: List[Problem] = []

    content = res.json()

    for raw_problem in content['stat_status_pairs']:
        stat = raw_problem['stat']

        # Skip hidden questions.
        if stat['question__hide']:
            continue

        problem = Problem(
            state=_from_api_state(raw_problem['status']),
            question_id=str(stat['question_id']),
            frontend_question_id=str(stat['frontend_question_id']),
            title=stat['question__title'],
            title_slug=stat['question__title_slug'],
            paid_only=raw_problem['paid_only'],
            ac_rate=stat['total_acs'] / stat['total_submitted'],
            difficulty=_from_api_difficulty(
                raw_problem['difficulty']['level']),
            frequency=raw_problem['frequency'],
            time_period_frequency=None,
        )

        problem_list.append(problem)

    log.debug('get_problem_list result: %s', pformat(problem_list))
    return problem_list


def get_problem(title_slug: str) -> ProblemDetail:
    _check_login()

    headers = _make_headers()
    headers['Referer'] = urls.PROBLEM_DESCRIPTION_URL.format(slug=title_slug)
    body = {'query': graphql_queries.GET_PROBLEM_QUERY,
            'variables': {'titleSlug': title_slug},
            'operationName': 'questionData'}

    log.info('get_problem request: POST %s headers=%s', urls.GRAPHQL_URL,
             headers)
    log.debug('get_problem request body: %s', body)
    res = _session.post(urls.GRAPHQL_URL, json=body, headers=headers)
    log.info('get_problem response: status=%s', res.status_code)
    log.debug('get_problem response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            messages.GET_PROBLEM_FAILURE.format(slug=title_slug))

    question = res.json()['data']['question']
    if question is None:
        raise LeetCodeOperationFailureError(
            messages.GET_PROBLEM_FAILURE.format(title_slug=title_slug))

    stats = json.loads(question['stats'])

    problem = ProblemDetail(
        question_id=question['questionId'],
        title=question['title'],
        title_slug=question['titleSlug'],
        frontend_question_id=question['questionFrontendId'],
        paid_only=question['isPaidOnly'],
        difficulty=_from_api_text_difficulty(question['difficulty']),
        description=question['content'],
        likes=question['likes'],
        dislikes=question['dislikes'],
        templates={},
        testable=question['enableRunCode'],
        testcase=question['sampleTestCase'],
        total_accepted=stats['totalAccepted'],
        total_submission=stats['totalSubmission'],
        ac_rate=stats['acRate'],
    )

    for snippet in question['codeSnippets']:
        problem.templates[snippet['langSlug']] = snippet['code']

    log.debug('get_problem result: %s', pformat(problem))
    return problem


def get_submission_list(title_slug: str) -> List[Submission]:
    _check_login()

    headers = _make_headers()
    headers['Referer'] = urls.SUBMISSION_REFERER_URL.format(slug=title_slug)

    body = {
        'operationName': 'Submissions',
        'variables': {
            'offset': 0,
            'limit': 50,
            'lastKey': None,
            'questionSlug': title_slug,
        },
        'query': graphql_queries.GET_SUBMISSION_LIST_QUERY,
    }

    url = urls.GRAPHQL_URL

    log.info('get_submission_list request: POST %s headers=%s', url, headers)
    log.debug('get_submission_list request body: %s', body)
    res = _session.post(url, headers=headers, json=body)
    log.info('get_submission_list response: status=%s', res.status_code)
    log.debug('get_submission_list response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            messages.GET_SUBMISSION_LIST_FAILURE.format(slug=title_slug))

    submission_list: List[Submission] = []

    raw_submission_list = res.json()['data']['submissionList']['submissions']

    for raw_submission in raw_submission_list:
        seconds_since_epoch = int(raw_submission['timestamp'])

        submission = Submission(
            id=raw_submission['id'],
            time=datetime.fromtimestamp(seconds_since_epoch),
            status=raw_submission['statusDisplay'],
            runtime=raw_submission['runtime'],
            lang=raw_submission['lang'],
            memory=raw_submission['memory'],
        )

        submission_list.append(submission)

    log.debug('get_submission_list result: %s', pformat(submission_list))
    return submission_list


SUBMISSION_STATUS_INT_TO_STR = {
    10: 'Accepted',
    11: 'Wrong Answer',
    12: 'Memory Limit Exceeded',
    13: 'Output Limit Exceeded',
    14: 'Time Limit Exceeded',
    15: 'Runtime Error',
    16: 'Internal Error',
    20: 'Compile Error',
    21: 'Unknown Error',
}


def _from_api_submission_status(status: int) -> str:
    if status in SUBMISSION_STATUS_INT_TO_STR:
        return SUBMISSION_STATUS_INT_TO_STR[status]
    return 'Unknown Status'


def _match_group_1(pattern: str, string: str) -> str:
    match_result = re.search(pattern, string)

    if not match_result:
        return messages.NOT_FOUND

    return match_result.group(1)


def _unescape_unicode(string: str) -> str:
    '''Unescape the string containing unicode escaped characters like '\\u0010'.
    '''
    return string.encode().decode('unicode_escape')


def _calc_percentile(distribution: List[Any], my_runtime: int) -> float:
    # The type of distribution is actually like List[TupleAsList[str, float]],
    # but since, Python does not support hetereogenous lists, the most precise
    # type is List[Any].
    percentile_sum = 0

    for runtime, portion in reversed(distribution):
        percentile_sum += portion
        if my_runtime >= int(runtime):
            break

    return percentile_sum


def _extract_runtime_percentile(text: str) -> float:
    runtime_distribution_match_result = re.search(
        "runtimeDistributionFormatted: '([^']*)'", text)

    if runtime_distribution_match_result:
        runtime_distribution_str = _unescape_unicode(
            runtime_distribution_match_result.group(1))
    else:
        runtime_distribution_str = '{"distribution": []}'

    runtime_distribution = json.loads(runtime_distribution_str)

    # There are two "runtime" appearing in the JavaScript code. The first
    # appearance is like "4 ms" and the second is like "4". We extract the
    # second apperance.
    first_runtime_match = re.search("runtime: '([^']*)'", text)

    if first_runtime_match:
        second_search_start = first_runtime_match.end()
    else:
        second_search_start = 0

    second_runtime_match = re.search("runtime: '([^']*)'",
                                     text[second_search_start:], 0)

    if second_runtime_match:
        runtime = int(second_runtime_match.group(1))
    else:
        runtime = 0

    return _calc_percentile(runtime_distribution['distribution'], runtime)


def get_submission(submission_id: str) -> SubmissionDetail:
    _check_login()

    headers = _make_headers()
    url = urls.SUBMISSION_URL.format(submission=submission_id)

    log.info('get_submission request: GET %s headers=%s', url, headers)
    res = _session.get(url, headers=headers)
    log.info('get_submission response: status=%s', res.status_code)
    log.debug('get_submission response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            messages.GET_SUBMISSION_FAILURE.format(submission=submission_id))

    # Extract the data from the JavaScript code in the HTML file.
    # This method is extremely hacky, since it tries to extract the information
    # directly from the JavaScript code using regular expressions.
    text = res.text

    raw_status = _match_group_1(r"status_code: parseInt\('([^']*)'", text)
    raw_data_input = _match_group_1("input : '([^']*)'", text)
    raw_actual_answer = _match_group_1("code_output : '([^']*)'", text)
    raw_expected_answer = _match_group_1("expected_output : '([^']*)'", text)
    edit_code_url = _match_group_1("editCodeUrl: '([^']*)'", text)
    raw_code = _match_group_1("submissionCode: '([^']*)'", text)

    submission = SubmissionDetail(
        id=submission_id,
        status=_from_api_submission_status(int(raw_status)),
        runtime=_match_group_1("runtime: '([^']*)'", text),
        passed=_match_group_1("total_correct : '([^']*)'", text),
        total=_match_group_1("total_testcases : '([^']*)'", text),
        data_input=_unescape_unicode(raw_data_input),
        actual_answer=_unescape_unicode(raw_actual_answer),
        expected_answer=_unescape_unicode(raw_expected_answer),
        problem_id=_match_group_1("questionId: '([^']*)'", text),
        title_slug=edit_code_url.split('/')[2],
        lang=_match_group_1("getLangDisplay: '([^']*)'", text),
        code=_unescape_unicode(raw_code),
        runtime_percentile=_extract_runtime_percentile(text),
    )

    log.debug('get_submission result: %s', pformat(submission))
    return submission


def test_code(request: SubmissionRequest) -> TestJob:
    _check_login()

    headers = _make_headers()
    headers['Referer'] = urls.PROBLEM_DESCRIPTION_URL.format(
        slug=request.title_slug)

    body = {'data_input': request.data_input,
            'lang': request.lang,
            'question_id': request.problem_id,
            'judge_type': 'small',
            'typed_code': request.code}

    url = urls.TEST_URL.format(slug=request.title_slug)

    log.info('test_code request: POST %s headers=%s', url, headers)
    log.debug('test_code request body: %s', body)

    res = _session.post(url, json=body, headers=headers)

    log.info('test_code response: status=%s', res.status_code)
    log.debug('test_code response body: %s', res.text)

    if res.status_code != 200:
        if res.status_code == 429:
            raise LeetCodeOperationFailureError(messages.TOO_FAST)
        raise LeetCodeOperationFailureError(
            messages.TEST_CODE_FAILURE.format(slug=request.title_slug))

    data = res.json()

    testing_job = TestJob(
        actual_id=data['interpret_id'],
        expected_id=data['interpret_expected_id'],
    )

    log.debug('test_code job: %s', pformat(testing_job))
    return testing_job


def submit_code(request: SubmissionRequest) -> str:
    _check_login()

    headers = _make_headers()
    headers['Referer'] = urls.PROBLEM_DESCRIPTION_URL.format(
        slug=request.title_slug)

    body = {'lang': request.lang,
            'question_id': request.problem_id,
            'typed_code': request.code}

    url = urls.SUBMIT_URL.format(slug=request.title_slug)

    log.info('submit_code request: POST %s headers=%s',
             url, headers)
    log.debug('submit_code request body: %s', body)

    res = _session.post(url, json=body, headers=headers)

    log.info('submit_code response: status="%s"',
             res.status_code)
    log.debug('submit_code response body: %s', res.text)

    if res.status_code != 200:
        if res.status_code == 429:
            raise LeetCodeOperationFailureError(messages.TOO_FAST)
        raise LeetCodeOperationFailureError(
            messages.SUBMIT_CODE_FAILURE.format(slug=request.title_slug))

    data = res.json()
    return str(data['submission_id'])


def _is_error_key(key: str) -> bool:
    return key.startswith('full_') and key.endswith('_error')


def retrieve_test_result(test_id: str) -> Union[RunningSubmission, TestResult]:
    _check_login()

    headers = _make_headers()

    url = urls.CHECK_URL.format(submission=test_id)

    log.info('retrieve_test_result request: GET %s headers=%s', url, headers)

    res = _session.get(url, headers=headers)

    log.info('retrieve_test_result response: status=%s', res.status_code)
    log.debug('retrieve_test_result response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            messages.RETRIEVE_SUBMISSION_RESULT_FAILURE.format(
                id=test_id))

    data = res.json()

    if data['state'] == 'PENDING':
        return RunningSubmission(state='PENDING')

    if data['state'] == 'STARTED':
        return RunningSubmission(state='STARTED')

    result = TestResult(
        status=_from_api_submission_status(data['status_code']),
        answer=data.get('code_answer', []),
        runtime=data['status_runtime'],
        errors=[value for key, value in data.items() if _is_error_key(key)],
        stdout=data['code_output'],
    )

    log.debug('retrieve_test_result result: %s', pformat(result))
    return result


def retrieve_submission_result(submission_id: str) \
        -> Union[RunningSubmission, SubmissionResult]:

    _check_login()

    headers = _make_headers()

    url = urls.CHECK_URL.format(submission=submission_id)

    log.info('retrieve_submission_result request: GET %s headers=%s',
             url, headers)

    res = _session.get(url, headers=headers)

    log.info('retrieve_submission_result response: status=%s', res.status_code)
    log.debug('retrieve_submission_result response body: %s', res.text)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            messages.RETRIEVE_SUBMISSION_RESULT_FAILURE.format(
                id=submission_id))

    data = res.json()

    if data['state'] == 'PENDING':
        return RunningSubmission(state='PENDING')

    if data['state'] == 'STARTED':
        return RunningSubmission(state='STARTED')

    result = SubmissionResult(
        status=_from_api_submission_status(data['status_code']),
        lang=data['lang'],
        runtime=data['status_runtime'],
        memory=data['status_memory'],
        errors=[value for key, value in data.items()
                if 'error' in key and value],
        stdout=data['std_output'],
        data_input=data.get('input'),
        actual_answer=data.get('code_output'),
        expected_answer=data.get('expected_output'),
        runtime_percentile=data.get('runtime_percentile'),
        memory_percentile=data.get('memory_percentile'),
    )

    log.debug('retrieve_submission_result result: %s', pformat(result))
    return result
