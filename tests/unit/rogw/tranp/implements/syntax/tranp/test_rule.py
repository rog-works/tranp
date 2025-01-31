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
				('rule', [
					('expand', '?'),
					('symbol', 'exp'),
					('symbol', 'primary'),
				]),
				('rule', [
					('expand', '?'),
					('symbol', 'primary'),
					('terms_or', [
						('symbol', 'relay'),
						('symbol', 'invoke'),
						('symbol', 'indexer'),
						('symbol', 'atom'),
					]),
				]),
				('rule', [
					('__empty__', ''),
					('symbol', 'relay'),
					('terms', [
						('symbol', 'primary'),
						('string', '"."'),
						('symbol', 'name'),
					]),
				]),
				('rule', [
					('__empty__', ''),
					('symbol', 'invoke'),
					('terms', [
						('symbol', 'primary'),
						('string', '"("'),
						('expr_opt', [
							('symbol', 'args'),
						]),
						('string', '")"'),
					]),
				]),
				('rule', [
					('__empty__', ''),
					('symbol', 'indexer'),
					('terms', [
						('symbol', 'primary'),
						('string', '"["'),
						('symbol', 'exp'),
						('string', '"]"'),
					]),
				]),
				('rule', [
					('__empty__', ''),
					('symbol', 'args'),
					('terms', [
						('symbol', 'exp'),
						('expr_rep', [
							('symbol', 'exp'),
							('repeat', '*'),
						]),
					]),
				]),
			]),
			'\n'.join([
				'entry := exp',
				'?exp := primary',
				'?primary := relay | invoke | indexer | atom',
				'relay := primary "." name',
				'invoke := primary "(" [args] ")"',
				'indexer := primary "[" exp "]"',
				'args := exp (exp)*',
			]),
		),
	])
	def test_from_ast(self, tree: TupleTree, expected: str) -> None:
		rules = Rules.from_ast(tree)
		self.assertEqual(expected, rules.pretty())
