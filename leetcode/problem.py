from enum import Enum
import json
import logging
from pprint import pformat
from typing import Dict, List, Optional

from leetcode import session
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.third_party import dataclass
from leetcode.urls import GRAPHQL_URL


class ProblemState(Enum):
    NEW = 'NEW'
    NOT_AC = 'NOT_AC'
    AC = 'AC'


class Difficulty(Enum):
    EASY = 'Easy'
    MEDIUM = 'Medium'
    HARD = 'Hard'
    UNKNOWN = 'Unknown'


@dataclass
class TimePeriodFrequency:
    six_months: float
    one_year: float
    two_years: float
    all_time: float


@dataclass
class Problem:
    state: ProblemState
    question_id: str
    frontend_question_id: str
    title: str
    title_slug: str
    paid_only: bool
    ac_rate: float
    difficulty: Difficulty
    frequency: Optional[float]
    time_period_frequency: Optional[TimePeriodFrequency]


@dataclass
class ProblemDetail:
    question_id: str
    frontend_question_id: str
    title: str
    title_slug: str
    paid_only: bool
    difficulty: Difficulty
    description: str
    templates: Dict[str, str]    # Key: language, value: template code
    testable: bool
    testcase: str
    total_accepted: str
    total_submission: str
    ac_rate: str
    likes: int
    dislikes: int



PROBLEM_DESCRIPTION_URL = 'https://leetcode.com/problems/{slug}/description'

PROBLEM_LIST_URL = 'https://leetcode.com/api/problems/all'


log = logging.getLogger(__name__)


def _from_api_text_difficulty(difficulty: str) -> Difficulty:
    if difficulty == 'Easy':
        return Difficulty.EASY
    if difficulty == 'Medium':
        return Difficulty.MEDIUM
    if difficulty == 'Hard':
        return Difficulty.HARD
    return Difficulty.UNKNOWN


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


def get_problem(title_slug: str) -> ProblemDetail:
    headers = {'Referer': PROBLEM_DESCRIPTION_URL.format(slug=title_slug)}

    body = {'query': GET_PROBLEM_QUERY,
            'variables': {'titleSlug': title_slug},
            'operationName': 'questionData'}

    res = session.post(GRAPHQL_URL, json=body, headers=headers)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError(
            'Could not get problem [{slug}]'.format(slug=title_slug))

    question = res.json()['data']['question']
    if question is None:
        raise LeetCodeOperationFailureError(
            'Could not get problem [{slug}]'.format(slug=title_slug))

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


def get_problem_list() -> List[Problem]:
    res = session.get(PROBLEM_LIST_URL)

    if res.status_code != 200:
        raise LeetCodeOperationFailureError('Could not get problem list')

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


GET_PROBLEM_QUERY = '''
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    boundTopicId
    title
    titleSlug
    content
    isPaidOnly
    difficulty
    likes
    dislikes
    isLiked
    similarQuestions
    contributors {
      username
      profileUrl
      avatarUrl
      __typename
    }
    langToValidPlayground
    topicTags {
      name
      slug
      translatedName
      __typename
    }
    companyTagStats
    codeSnippets {
      lang
      langSlug
      code
      __typename
    }
    stats
    hints
    solution {
      id
      canSeeDetail
      __typename
    }
    status
    sampleTestCase
    metaData
    judgerAvailable
    judgeType
    mysqlSchemas
    enableRunCode
    enableTestMode
    envInfo
    libraryUrl
    __typename
  }
}
'''.strip()
