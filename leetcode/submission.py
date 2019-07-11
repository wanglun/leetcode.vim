from datetime import datetime
from enum import Enum
import json
import logging
import re
from pprint import pformat
from typing import Any, List

from leetcode import session
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.third_party import dataclass
from leetcode.urls import GRAPHQL_URL


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


class SubmissionStatus(Enum):
    ACCEPTED = 'Accepted'
    WRONG_ANSWER = 'Wrong Answer'
    MEMORY_LIMIT_EXCEEDED = 'Memory Limit Exceeded'
    OUTPUT_LIMIT_EXCEEDED = 'Output Limit Exceeded'
    TIME_LIMIT_EXCEEDED = 'Time Limit Exceeded'
    RUNTIME_ERROR = 'Runtime Error'
    INTERNAL_ERROR = 'Internal Error'
    COMPILE_ERROR = 'Compile Error'
    UNKNOWN_ERROR = 'Unknown Error'

    @staticmethod
    def from_int(status: int) -> 'SubmissionStatus':
        if status in SUBMISSION_STATUS_INT_TO_STR:
            return SubmissionStatus(SUBMISSION_STATUS_INT_TO_STR[status])
        return SubmissionStatus.UNKNOWN_ERROR

    @staticmethod
    def from_str(status: str) -> 'SubmissionStatus':
        try:
            return SubmissionStatus(status)
        except ValueError:
            return SubmissionStatus.UNKNOWN_ERROR


@dataclass
class Submission:
    id: str
    time: datetime
    lang: str
    runtime: str
    memory: str
    status: SubmissionStatus


@dataclass
class SubmissionDetail:
    id: str
    status: SubmissionStatus
    runtime: str
    passed: str
    total: str
    data_input: str
    actual_answer: str
    expected_answer: str
    problem_id: str
    title_slug: str
    lang: str
    code: str
    runtime_percentile: float


SUBMISSION_REFERER_URL = 'https://leetcode.com/problems/{slug}/submissions/'

SUBMISSION_URL = 'https://leetcode.com/submissions/detail/{submission}/'

log = logging.getLogger(__name__)


def get_submission_list(title_slug: str) -> List[Submission]:
    headers = {
        'Referer': SUBMISSION_REFERER_URL.format(slug=title_slug)
    }

    body = {
        'operationName': 'Submissions',
        'variables': {
            'offset': 0,
            'limit': 50,
            'lastKey': None,
            'questionSlug': title_slug,
        },
        'query': GET_SUBMISSION_LIST_QUERY,
    }

    res = session.post(GRAPHQL_URL, headers=headers, json=body)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            'Could not get submission list of [{slug}]'.format(slug=title_slug))

    submission_list: List[Submission] = []

    raw_submission_list = res.json()['data']['submissionList']['submissions']

    for raw_submission in raw_submission_list:
        seconds_since_epoch = int(raw_submission['timestamp'])

        submission = Submission(
            id=raw_submission['id'],
            time=datetime.fromtimestamp(seconds_since_epoch),
            status=SubmissionStatus.from_str(raw_submission['statusDisplay']),
            runtime=raw_submission['runtime'],
            lang=raw_submission['lang'],
            memory=raw_submission['memory'],
        )

        submission_list.append(submission)

    log.debug('get_submission_list result: %s', pformat(submission_list))
    return submission_list


def _match_group_1(pattern: str, string: str) -> str:
    match_result = re.search(pattern, string)

    if not match_result:
        return 'Attribute not found'

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
    url = SUBMISSION_URL.format(submission=submission_id)

    res = session.get(url)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            'Could not get submission [{submission}]'.format(
                submission=submission_id))

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
        status=SubmissionStatus.from_int(int(raw_status)),
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


GET_SUBMISSION_LIST_QUERY = '''
query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
    lastKey
    hasNext
    submissions {
      id
      statusDisplay
      lang
      runtime
      timestamp
      url
      isPending
      memory
      __typename
    }
    __typename
  }
}
'''.strip()
