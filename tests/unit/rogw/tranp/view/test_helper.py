from typing import Any
from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.helper import DecoratorHelper, DecoratorQuery


class TestDecoratorParser(TestCase):
	@data_provider([
		('abc()', {'path': 'abc', 'args': {}, 'arg': ''}),
		('Embed.prop("a")', {'path': 'Embed.prop', 'args': {'0': '"a"'}, 'arg': '"a"'}),
		('Embed.alias("a", prefix=true)', {'path': 'Embed.alias', 'args': {'0': '"a"', 'prefix': 'true'}, 'arg': '"a"'}),
	])
	def test_schema(self, decorator: str, expected: dict[str, Any]) -> None:
		instance = DecoratorHelper(decorator)
		self.assertEqual(instance.path, expected['path'])
		self.assertEqual(instance.args, expected['args'])
		self.assertEqual(instance.arg, expected['arg'])

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
