from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from leetcode.third_party import dataclass


class ProblemState(Enum):
    NEW = 'NEW'
    NOT_AC = 'NOT_AC'
    AC = 'AC'


class Difficulty(Enum):
    EASY = 'EASY'
    MEDIUM = 'MEDIUM'
    HARD = 'HARD'
    UNKNOWN = 'UNKNOWN'


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


@dataclass
class Submission:
    id: str
    time: datetime
    lang: str
    runtime: str
    memory: str
    status: str


@dataclass
class SubmissionDetail:
    id: str
    status: str
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


@dataclass
class TestJob:
    actual_id: str
    expected_id: str


@dataclass
class SubmissionRequest:
    problem_id: str
    title_slug: str
    lang: str
    code: str
    data_input: str


@dataclass
class RunningSubmission:
    state: str


@dataclass
class TestResult:
    status: str
    answer: List[str]
    runtime: str
    errors: List[str]
    stdout: List[str]


@dataclass
class SubmissionResult:
    status: str
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
