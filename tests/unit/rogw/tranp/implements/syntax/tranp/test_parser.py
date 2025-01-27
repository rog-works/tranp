from typing import Any
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import Lexer, rules
from rogw.tranp.test.helper import data_provider


class TestParser(TestCase):
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
		actual = Lexer(rules_).parse(source, 'entry')

		try:
			self.assertEqual(expected['ast'], actual)
		except AssertionError:
			print('AST unmatch. actual: {actual}')
			raise
