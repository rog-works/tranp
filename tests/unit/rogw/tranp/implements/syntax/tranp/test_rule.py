from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.ast import TupleTree
from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.test.helper import data_provider


class TestRules(TestCase):
	@data_provider([
		(
			('entry', [
				('rule', [
					('__empty__', ''),
					('symbol', 'entry'),
					('symbol', 'exp'),
				]),
			]),
			'\n'.join([
				'entry := exp',
			]),
		),
	])
	def test_from_ast(self, tree: TupleTree, expected: str) -> None:
		rules = Rules.from_ast(tree)
		self.assertEqual(expected, rules.pretty())
