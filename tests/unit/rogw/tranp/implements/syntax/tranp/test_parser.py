from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import SyntaxParser
from rogw.tranp.implements.syntax.tranp.rules import python_rules
from rogw.tranp.test.helper import data_provider


class TestSyntaxParser(TestCase):
	@data_provider([
		(
			'a',
			('entry', [
				('var', [
					('name', 'a'),
				]),
			]),
		),
	])
	def test_parse(self, source: str, expected: tuple) -> None:
		rules = python_rules()
		actual = SyntaxParser(rules).parse(source, 'entry')
		self.assertEqual(expected, actual)
