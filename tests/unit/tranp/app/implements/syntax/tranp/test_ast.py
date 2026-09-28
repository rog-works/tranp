from unittest import TestCase

from tranp.app.implements.syntax.tranp.ast import ASTNormal
from tranp.app.implements.syntax.tranp.syntax import SyntaxParser
from tranp.app.test.helper import data_provider
from tranp.data.syntax.py_rules import py_rules


class TestASTTree(TestCase):
	@data_provider([
		('self.data.models', [
			(0, 'name', 'self'),
			(1, 'var', [0]),
			(2, 'name', 'data'),
			(3, 'relay', [1, 2]),
			(4, 'name', 'models'),
			(5, 'relay', [3, 4]),
			(6, 'entry', [5]),
		]),
	])
	def test_normalize(self, source: str, expected: list[ASTNormal]) -> None:
		parser = SyntaxParser(py_rules())
		ast = parser.parse(source, 'entry')
		actual = ast.normalize()
		self.assertEqual(expected, actual)
