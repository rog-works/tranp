import json
from typing import Any
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import Lexer, rules
from rogw.tranp.test.helper import data_provider


class TestParser(TestCase):
	@data_provider([
		('a.b.c', {
			'ast': ('relay', [
				('relay', [
					('var', [
						('name', 'a'),
					]),
					('name', 'b'),
				]),
				('name', 'c'),
			]),
		}),
	])
	def test_parse(self, source: str, expected: dict[str, Any]) -> None:
		rules_ = rules()
		actual = Lexer(rules_).parse(source, 'entry')
		print(json.dumps(actual))
		self.assertEqual(expected['ast'], actual)
