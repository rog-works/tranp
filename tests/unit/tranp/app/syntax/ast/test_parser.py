from unittest import TestCase

from tests.unit.tranp.app.syntax.ast.test_entry import EntryImpl

from tranp.app.lang.annotation import duck_typed
from tranp.app.syntax.ast.parser import SyntaxParser


class SyntaxParserImpl:
	@duck_typed(SyntaxParser)
	def parse(self, module_path: str) -> EntryImpl:
		return EntryImpl(('root', []))


class TestSyntaxParser(TestCase):
	def test_parse(self) -> None:
		self.assertEqual(SyntaxParserImpl().parse('').name, 'root')
