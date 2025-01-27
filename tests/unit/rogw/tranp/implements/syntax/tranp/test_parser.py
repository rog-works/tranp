from typing import Any
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import SyntaxParser, TokenParser, rules
from rogw.tranp.test.helper import data_provider


class TestTokenParser(TestCase):
	@data_provider([
		('a.b.c', ['a', '.', 'b', '.', 'c']),
		('?a _b', ['?', 'a', '_b']),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		actual = TokenParser.parse(source)
		self.assertEqual(expected, [token.string for token in actual])


class TestSyntaxParser(TestCase):
	@data_provider([
		('a.b.c', {
			'ast': ('entry', [
				('relay', [
					('relay', [
						('var', [
							('name', 'a'),
						]),
						('name', 'b'),
					]),
					('name', 'c'),
				]),
			]),
		}),
	])
	def test_parse(self, source: str, expected: dict[str, Any]) -> None:
		rules_ = rules()
		actual = SyntaxParser(rules_).parse(source, 'entry')

		try:
			self.assertEqual(expected['ast'], actual)
		except AssertionError:
			print('AST unmatch. actual: {actual}')
			raise
