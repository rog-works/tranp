from typing import Any
from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.helper import DecoratorHelper, DecoratorQuery


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
		if len(expected['args']) > 0:
			first_key = list(expected['args'].keys())[0]
			self.assertEqual(instance.arg, expected['args'][first_key])
			for index, expected_at in enumerate(expected['args'].items()):
				expected_key, expected_value = expected_at
				self.assertEqual(instance.arg_at(index), expected_value)
				self.assertEqual(instance.arg_by(expected_key), expected_value)

	@data_provider([
		('abc()', ['abc'], {}, True),
		('abc()', ['a', 'b', 'c'], {}, False),
		('Embed.prop("a")', ['Embed.prop'], {}, True),
		('Embed.prop("a")', ['Embed.prop'], {'0': '"a"'}, True),
		('Embed.prop("abc")', ['Embed.prop'], {'0': '"a"'}, False),
	])
	def test_any(self, decorator: str, paths: list[str], args: dict[str, str], expected: bool) -> None:
		actual = DecoratorHelper(decorator).any(*paths, **args)
		self.assertEqual(actual, expected)

	@data_provider([
		('abc()', r'^abc', True),
		('abc()', r'^abc\(\)$', True),
	])
	def test_match(self, decorator: str, pattern: str, expected: bool) -> None:
		actual = DecoratorHelper(decorator).match(pattern)
		self.assertEqual(actual, expected)


class TestDecoratorQuery(TestCase):
	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], {}),
	])
	def test___iter__(self, decorators: list[str], paths: list[str], args: dict[str, str]) -> None:
		actual = [helper.decorator for helper in DecoratorQuery(decorators)]
		self.assertEqual(actual, decorators)

	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], {}, ['abc()']),
	])
	def test_filter(self, decorators: list[str], paths: list[str], args: dict[str, str], expected: list[str]) -> None:
		actual = [helper.decorator for helper in DecoratorQuery(decorators).filter(*paths, **args)]
		self.assertEqual(actual, expected)

	@data_provider([
		(['a()', 'ab()', 'abc()'], ['abc'], {}, True),
	])
	def test_any(self, decorators: list[str], paths: list[str], args: dict[str, str], expected: bool) -> None:
		actual = DecoratorQuery(decorators).any(*paths, **args)
		self.assertEqual(actual, expected)

	@data_provider([
		(['a()', 'ab()', 'abc()'], 'abc', True),
	])
	def test_match(self, decorators: list[str], pattern: str, expected: bool) -> None:
		actual = DecoratorQuery(decorators).match(pattern)
		self.assertEqual(actual, expected)
