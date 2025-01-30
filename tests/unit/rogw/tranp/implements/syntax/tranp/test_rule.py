from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.ast import ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.implements.syntax.tranp.token import Token, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestRules(TestCase):
	@data_provider([
		(
			ASTTree('entry', [
				ASTTree('rule', [
					ASTToken.empty(),
					ASTToken('symbol', Token(TokenTypes.Name, 'entry')),
					ASTToken('symbol', Token(TokenTypes.Name, 'exp')),
				]),
			]),
			'\n'.join([
				'entry := exp',
			]),
		),
	])
	def test_from_ast(self, tree: ASTTree, expected: str) -> None:
		rules = Rules.from_ast(tree)
		self.assertEqual(expected, rules.pretty())
