from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.ast import ASTNormal
from rogw.tranp.implements.syntax.tranp.rules import python_rules
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.test.helper import data_provider


class TestASTTree(TestCase):
	@data_provider([
		('self.data.models', [
			(0, 'name', 'self', []),
			(1, 'var', '', [0]),
			(2, 'name', 'data', []),
			(3, 'relay', '', [1, 2]),
			(4, 'name', 'models', []),
			(5, 'relay', '', [3, 4]),
			(6, 'entry', '', [5]),
		]),
	])
	def test_normalize(self, source: str, expected: list[ASTNormal]) -> None:
		parser = SyntaxParser(python_rules())
		ast = parser.parse(source, 'entry')
		actual = ast.normalize()
		self.assertEqual(expected, actual)
