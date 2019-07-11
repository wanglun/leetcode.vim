import logging
from pprint import pformat
from typing import List, Optional, Union

from leetcode import session
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.problem import PROBLEM_DESCRIPTION_URL
from leetcode.submission import SubmissionStatus
from leetcode.third_party import dataclass


@dataclass
class SubmissionRequest:
    problem_id: str
    title_slug: str
    lang: str
    code: str
    data_input: str


@dataclass
class TestJob:
    actual_id: str
    expected_id: str


@dataclass
class RunningSubmission:
    state: str


@dataclass
class TestResult:
    status: SubmissionStatus
    answer: List[str]
    runtime: str
    errors: List[str]
    stdout: List[str]


@dataclass
class SubmissionResult:
    status: SubmissionStatus
    lang: str
    runtime: str
    memory: str
    errors: List[str]
    stdout: str

    # Used if the submission didn't pass all the tests.
    data_input: Optional[str] = None
    actual_answer: Optional[str] = None
    expected_answer: Optional[str] = None

    # Used if the submission passed all the tests.
    runtime_percentile: Optional[float] = None
    memory_percentile: Optional[float] = None


TEST_URL = 'https://leetcode.com/problems/{slug}/interpret_solution/'

SUBMIT_URL = 'https://leetcode.com/problems/{slug}/submit/'

CHECK_URL = 'https://leetcode.com/submissions/detail/{submission}/check/'

log = logging.getLogger(__name__)


def _is_error_key(key: str) -> bool:
    return key.startswith('full_') and key.endswith('_error')


def test_code(request: SubmissionRequest) -> TestJob:
    headers = {
        'Referer': PROBLEM_DESCRIPTION_URL.format(slug=request.title_slug)
    }

    body = {'data_input': request.data_input,
            'lang': request.lang,
            'question_id': request.problem_id,
            'judge_type': 'small',
            'typed_code': request.code}

    url = TEST_URL.format(slug=request.title_slug)

    res = session.post(url, json=body, headers=headers)

    if res.status_code != 200:
        if res.status_code == 429:
            raise LeetCodeOperationFailureError('Submitting too fast')
        raise LeetCodeOperationFailureError(
            'Could not test the code [{slug}]'.format(slug=request.title_slug))

    data = res.json()

    testing_job = TestJob(
        actual_id=data['interpret_id'],
        expected_id=data['interpret_expected_id'],
    )

    log.debug('test_code job: %s', pformat(testing_job))
    return testing_job


def retrieve_test_result(test_id: str) -> Union[RunningSubmission, TestResult]:
    url = CHECK_URL.format(submission=test_id)

    res = session.get(url)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            'Could not retrieve result of submission [{id}]'.format(id=test_id))

    data = res.json()

    if data['state'] == 'PENDING':
        return RunningSubmission(state='PENDING')

    if data['state'] == 'STARTED':
        return RunningSubmission(state='STARTED')

    result = TestResult(
        status=SubmissionStatus.from_int(data['status_code']),
        answer=data.get('code_answer', []),
        runtime=data['status_runtime'],
        errors=[value for key, value in data.items() if _is_error_key(key)],
        stdout=data['code_output'],
    )

    log.debug('retrieve_test_result result: %s', pformat(result))
    return result


def submit_code(request: SubmissionRequest) -> str:
    headers = {
        'Referer': PROBLEM_DESCRIPTION_URL.format(slug=request.title_slug)
    }

    body = {'lang': request.lang,
            'question_id': request.problem_id,
            'typed_code': request.code}

    url = SUBMIT_URL.format(slug=request.title_slug)

    res = session.post(url, json=body, headers=headers)

    if res.status_code != 200:
        if res.status_code == 429:
            raise LeetCodeOperationFailureError('Submitting too fast')
        raise LeetCodeOperationFailureError(
            'Could not submit the code [{slug}]'.format(
                slug=request.title_slug))

    data = res.json()
    return str(data['submission_id'])


def retrieve_submission_result(submission_id: str) \
        -> Union[RunningSubmission, SubmissionResult]:
    url = CHECK_URL.format(submission=submission_id)

    res = session.get(url)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            'Could not retrieve submission result [{id}]'.format(
                id=submission_id))

    data = res.json()

    if data['state'] == 'PENDING':
        return RunningSubmission(state='PENDING')

    if data['state'] == 'STARTED':
        return RunningSubmission(state='STARTED')

    result = SubmissionResult(
        status=SubmissionStatus.from_int(data['status_code']),
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
