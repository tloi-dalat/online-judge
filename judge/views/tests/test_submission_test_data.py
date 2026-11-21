from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from judge.models import ProblemTestCase
from judge.models.tests.util import create_problem
from judge.views.submission import get_test_data_by_position


class TestDataByPositionTestCase(TestCase):
    def setUp(self):
        self.problem = create_problem('positions')
        self.order = 0
        self.names = {}

    def add(self, name='', type='C', is_pretest=False, is_example=False):
        self.order += 1
        case = ProblemTestCase.objects.create(dataset=self.problem, order=self.order, type=type,
                                              input_file=f'{name}.in' if name else '', is_pretest=is_pretest,
                                              is_example=is_example)
        if name:
            self.names[case.id] = name

    def lookup(self, pretested, can_view_test=True, pretests_in_test_cases=False):
        metadata = {'testcases': dict(self.names), 'pretests_in_test_cases': pretests_in_test_cases}
        with patch('judge.views.submission.get_problem_metadata', return_value=metadata):
            return get_test_data_by_position(SimpleNamespace(problem=self.problem, is_pretested=pretested),
                                             can_view_test)

    def test_without_pretests(self):
        self.add('a')
        self.add('b', is_example=True)
        self.add('c')
        cases, examples, examples_data = self.lookup(pretested=False)
        self.assertEqual(cases, {1: 'a', 2: 'b', 3: 'c'})
        self.assertEqual(examples, {2})
        self.assertEqual(examples_data, {2: 'b'})

    def test_pretest_run_only_numbers_pretests(self):
        self.add('a')
        self.add('b', is_pretest=True)
        self.add('c', is_example=True)
        cases, examples, _ = self.lookup(pretested=True)
        self.assertEqual(cases, {1: 'b'})
        self.assertEqual(examples, set())

    def test_full_run_puts_pretests_first(self):
        self.add('a')
        self.add('b', is_pretest=True)
        self.add('c', is_example=True)
        cases, examples, _ = self.lookup(pretested=False)
        self.assertEqual(cases, {1: 'b', 2: 'a', 3: 'c'})
        self.assertEqual(examples, {3})

    def test_batches_count_each_case(self):
        self.add(type='S', is_pretest=True)
        self.add('d', is_pretest=True, is_example=True)
        self.add('e', is_pretest=True)
        self.add(type='E', is_pretest=True)
        self.add('f')
        self.assertEqual(self.lookup(pretested=True)[0], {1: 'd', 2: 'e'})
        cases, examples, _ = self.lookup(pretested=False)
        self.assertEqual(cases, {1: 'd', 2: 'e', 3: 'f'})
        self.assertEqual(examples, {1})

    def test_pretests_in_test_cases_keep_editor_order(self):
        self.add('a')
        self.add(type='S')
        self.add('b')
        self.add('c', is_pretest=True, is_example=True)
        self.add(type='E')
        self.add('d', is_pretest=True)
        self.assertEqual(self.lookup(pretested=True, pretests_in_test_cases=True)[0], {1: 'c', 2: 'd'})
        cases, examples, _ = self.lookup(pretested=False, pretests_in_test_cases=True)
        self.assertEqual(cases, {1: 'a', 2: 'b', 3: 'c', 4: 'd'})
        self.assertEqual(examples, {3})

    def test_cases_without_input_file_still_take_a_position(self):
        self.add()
        self.add('b')
        self.assertEqual(self.lookup(pretested=False)[0], {2: 'b'})

    def test_hidden_test_data_keeps_examples(self):
        self.add('a', is_example=True)
        self.add('b')
        cases, examples, examples_data = self.lookup(pretested=False, can_view_test=False)
        self.assertEqual(cases, {})
        self.assertEqual(examples_data, {1: 'a'})

    def test_manually_managed_problem(self):
        self.add('a', is_example=True)
        self.problem.is_manually_managed = True
        self.assertEqual(self.lookup(pretested=False), ({}, set(), {}))
