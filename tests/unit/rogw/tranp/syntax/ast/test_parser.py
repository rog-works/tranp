from unittest import TestCase

from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.syntax.ast.parser import SyntaxParser
from tests.unit.rogw.tranp.syntax.ast.test_entry import EntryImpl


class SyntaxParserImpl:
	@duck_typed(SyntaxParser)
	def parse(self, module_path: str) -> EntryImpl:
		return EntryImpl(('root', []))


class TestSyntaxParser(TestCase):
	def test_parse(self) -> None:
		self.assertEqual(SyntaxParserImpl().parse('').name, 'root')
