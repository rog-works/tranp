from typing import Any
from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.helper.decorator import DecoratorHelper, DecoratorQuery


class TestDecoratorParser(TestCase):
	@data_provider([
		('abc()', {'path': 'abc', 'args': {}}),
		('Embed.prop("a")', {'path': 'Embed.prop', 'args': {'0': '"a"'}}),
		('Embed.alias("a", prefix=true)', {'path': 'Embed.alias', 'args': {'0': '"a"', 'prefix': 'true'}}),
	])
	def test_schema(self, decorator: str, expected: dict[str, Any]) -> None:
		instance = DecoratorHelper(decorator)
		self.assertEqual(instance.decorator, decorator)
		self.assertEqual(instance.path, expected['path'])
		self.assertEqual(instance.args, expected['args'])
		self.assertEqual(instance.join_args, decorator[decorator.find('(') + 1:-1])
		if len(expected['args']) > 0:
			first_key = list(expected['args'].keys())[0]
			self.assertEqual(instance.arg, expected['args'][first_key])
			for index, expected_at in enumerate(expected['args'].items()):
				expected_key, expected_value = expected_at
				self.assertEqual(instance.arg_at(index), expected_value)
				self.assertEqual(instance.arg_by(expected_key), expected_value)

	@data_provider([
		('abc()', ['abc'], True),
		('abc()', ['a', 'b', 'c'], False),
		('Embed.prop("a")', ['Embed.prop'], True),
	])
	def test_any(self, decorator: str, paths: list[str], expected: bool) -> None:
		actual = DecoratorHelper(decorator).any(*paths)
		self.assertEqual(actual, expected)

	@data_provider([
		('abc()', r'^abc', True),
		('abc()', r'^abc\(\)$', True),
	])
	def test_match(self, decorator: str, pattern: str, expected: bool) -> None:
		actual = DecoratorHelper(decorator).match(pattern)
		self.assertEqual(actual, expected)

	@data_provider([
		('abc("abc")', '"abc"', True),
		('abc("abc")', 'abc', True),
		('abc("abc")', '"a"', False),
	])
	def test_find_args(self, decorator: str, subject: str, expected: bool) -> None:
		actual = DecoratorHelper(decorator).any_args(subject)
		self.assertEqual(actual, expected)

	@data_provider([
		('abc()', r'^$', True),
		('abc("a")', r'^"a"$', True),
		('abc("a")', r'^a$', False),
	])
	def test_match_args(self, decorator: str, pattern: str, expected: bool) -> None:
		actual = DecoratorHelper(decorator).match_args(pattern)
		self.assertEqual(actual, expected)


class TestDecoratorQuery(TestCase):
	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], {}),
	])
	def test_schema(self, decorators: list[str], paths: list[str], args: dict[str, str]) -> None:
		instance = DecoratorQuery.parse(decorators)
		self.assertEqual([helper.decorator for helper in instance], decorators)
		for i in range(len(decorators)):
			self.assertEqual(instance[i].decorator, decorators[i])

	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], ['abc()']),
	])
	def test_any(self, decorators: list[str], paths: list[str], expected: list[str]) -> None:
		actual = [helper.decorator for helper in DecoratorQuery.parse(decorators).any(*paths)]
		self.assertEqual(actual, expected)

	@data_provider([
		(['a()', 'ab()', 'abc()'], 'abc', ['abc()']),
	])
	def test_match(self, decorators: list[str], pattern: str, expected: bool) -> None:
		actual = [helper.decorator for helper in DecoratorQuery.parse(decorators).match(pattern)]
		self.assertEqual(actual, expected)

	@data_provider([
		(['a("abc")', 'ab("a")', 'abc("a")'], '"a"', ['ab("a")', 'abc("a")']),
	])
	def test_any_args(self, decorators: list[str], subject: str, expected: list[str]) -> None:
		actual = [helper.decorator for helper in DecoratorQuery.parse(decorators).any_args(subject)]
		self.assertEqual(actual, expected)

	@data_provider([
		(['a("abc")', 'ab("a")', 'abc("a")'], r'^"a"$', ['ab("a")', 'abc("a")']),
	])
	def test_match_args(self, decorators: list[str], pattern: str, expected: list[str]) -> None:
		actual = [helper.decorator for helper in DecoratorQuery.parse(decorators).match_args(pattern)]
		self.assertEqual(actual, expected)

	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], True),
	])
	def test_contains(self, decorators: list[str], paths: list[str], expected: bool) -> None:
		actual = DecoratorQuery.parse(decorators).contains(*paths)
		self.assertEqual(actual, expected)
