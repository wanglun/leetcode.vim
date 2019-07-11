import unittest

from leetcode.problem import Problem, Difficulty, ProblemState, \
    TimePeriodFrequency
from leetcode.utils import to_plain


class UtilsTest(unittest.TestCase):

    COMPLEX = Problem(
        state=ProblemState.NOT_AC,
        question_id='12',
        frontend_question_id='13',
        title='Some title',
        title_slug='some-title',
        paid_only=False,
        ac_rate=0.25,
        difficulty=Difficulty.MEDIUM,
        frequency=None,
        time_period_frequency=TimePeriodFrequency(0.3, 3, 14, 4.5),
    )

    COMPLEX_PLAIN = {
        'state': 'NOT_AC',
        'question_id': '12',
        'frontend_question_id': '13',
        'title': 'Some title',
        'title_slug': 'some-title',
        'paid_only': False,
        'ac_rate': 0.25,
        'difficulty': 'Medium',
        'frequency': None,
        'time_period_frequency': {
            'six_months': 0.3,
            'one_year': 3,
            'two_years': 14,
            'all_time': 4.5,
        }
    }

    def test_primitive_to_plain(self):
        self.assertEqual(to_plain(3), 3)
        self.assertEqual(to_plain(True), True)
        self.assertEqual(to_plain(None), None)
        self.assertEqual(to_plain(3.5), 3.5)
        self.assertEqual(to_plain('str'), 'str')

    def test_list_to_plain(self):
        self.assertEqual(to_plain([]), [])
        self.assertEqual(to_plain([1, 'a', False]), [1, 'a', False])

    def test_dict_to_plain(self):
        self.assertEqual(to_plain({}), {})
        self.assertEqual(to_plain({'a': 1, None: 3.5}), {'a': 1, None: 3.5})

    def test_enum_to_plain(self):
        self.assertEqual(to_plain(Difficulty.HARD), 'Hard')

    def test_dataclass_to_plain(self):
        self.assertEqual(to_plain(self.COMPLEX.time_period_frequency),
                         self.COMPLEX_PLAIN['time_period_frequency'])

    def test_complex_to_plain(self):
        self.assertEqual(to_plain(self.COMPLEX), self.COMPLEX_PLAIN)
