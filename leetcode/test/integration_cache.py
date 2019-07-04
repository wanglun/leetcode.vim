from copy import deepcopy
from datetime import datetime, timedelta
import os
import os.path
import pickle
import unittest

from leetcode import cache, config
from leetcode.test.test_cache import CacheTest

class CacheIntegrationTest(unittest.TestCase):

    original_cache_path: str = ''

    TEST_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'test_cache.pkl')

    CACHED_DATA = CacheTest.CACHED_DATA

    def setUp(self):
        self.original_cache_path = config.CACHE_PATH
        config.CACHE_PATH = self.TEST_CACHE_PATH
        if os.access(self.TEST_CACHE_PATH, os.F_OK):
            os.remove(self.TEST_CACHE_PATH)

    def tearDown(self):
        config.CACHE_PATH = self.original_cache_path
        if os.access(self.TEST_CACHE_PATH, os.F_OK):
            os.remove(self.TEST_CACHE_PATH)

    def test_load_problem_list_from_new_cache(self):
        problem_list = cache.load_problem_list()
        self.assertIsNone(problem_list)

    def test_load_problem_list_from_existing_cache(self):
        with open(self.TEST_CACHE_PATH, 'wb') as cache_file:
            pickle.dump(self.CACHED_DATA, cache_file,
                        protocol=pickle.HIGHEST_PROTOCOL)

        problem_list = cache.load_problem_list()

        self.assertEqual(problem_list[0].question_id, '2')

    def test_load_problem_list_from_expired_cache(self):
        cached_data = deepcopy(self.CACHED_DATA)
        cached_data.expired_at = datetime.now() - timedelta(days=1)

        with open(self.TEST_CACHE_PATH, 'wb') as cache_file:
            pickle.dump(cached_data, cache_file,
                        protocol=pickle.HIGHEST_PROTOCOL)

        problem_list = cache.load_problem_list()

        self.assertIsNone(problem_list)

    def test_save_problem_list_to_new_cache(self):
        cache.save_problem_list(self.CACHED_DATA.problem_list)

        problem_list = cache.load_problem_list()

        self.assertEqual(problem_list[0].question_id, '2')

    def test_save_problem_list_to_existing_cache(self):
        with open(self.TEST_CACHE_PATH, 'wb') as cache_file:
            pickle.dump(self.CACHED_DATA, cache_file,
                        protocol=pickle.HIGHEST_PROTOCOL)

        cached_data = deepcopy(self.CACHED_DATA)
        cached_data.problem_list[0].question_id = '3'

        cache.save_problem_list(cached_data.problem_list)

        problem_list = cache.load_problem_list()

        self.assertEqual(problem_list[0].question_id, '3')
