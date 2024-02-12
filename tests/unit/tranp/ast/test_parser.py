from unittest import TestCase

from tranp.ast.parser import SyntaxParser
from tranp.lang.implementation import implements
from tests.unit.tranp.ast.test_entry import EntryImpl


class SyntaxParserImpl(SyntaxParser):
	@implements
	def parse(self, module_path: str) -> EntryImpl:
		return EntryImpl(('root', []))


class TestSyntaxParser(TestCase):
	def test_parse(self) -> None:
		self.assertEqual(SyntaxParserImpl().parse('').name, 'root')
