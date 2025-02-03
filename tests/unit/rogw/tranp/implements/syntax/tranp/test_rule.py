from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.ast import TupleTree
from rogw.tranp.implements.syntax.tranp.rule import Comps, Pattern, Roles, Rules
from rogw.tranp.test.helper import data_provider


class TestPattern(TestCase):
	@data_provider([
		('"a"', (Roles.Terminal, Comps.Equals)),
		('/a/', (Roles.Terminal, Comps.Regexp)),
		('a', (Roles.Symbol, Comps.NoComp)),
	])
	def test_make(self, expression: str, expected: str) -> None:
		actual = Pattern.make(expression)
		self.assertEqual(expected, (actual.role, actual.comp))


class TestRules(TestCase):
	@data_provider([
		(
			('entry', [
				('rule', [
					('symbol', 'entry'),
					('__empty__', ''),
					('symbol', 'exp'),
				]),
				('rule', [
					('symbol', 'exp'),
					('unwrap', '1'),
					('symbol', 'primary'),
				]),
				('rule', [
					('symbol', 'primary'),
					('unwrap', '1'),
					('terms_or', [
						('symbol', 'relay'),
						('symbol', 'invoke'),
						('symbol', 'indexer'),
						('symbol', 'atom'),
					]),
				]),
				('rule', [
					('symbol', 'relay'),
					('__empty__', ''),
					('terms', [
						('symbol', 'primary'),
						('string', '"."'),
						('symbol', 'name'),
					]),
				]),
				('rule', [
					('symbol', 'invoke'),
					('__empty__', ''),
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
					('symbol', 'indexer'),
					('__empty__', ''),
					('terms', [
						('symbol', 'primary'),
						('string', '"["'),
						('symbol', 'exp'),
						('string', '"]"'),
					]),
				]),
				('rule', [
					('symbol', 'args'),
					('__empty__', ''),
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
				'exp[1] := primary',
				'primary[1] := relay | invoke | indexer | atom',
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
