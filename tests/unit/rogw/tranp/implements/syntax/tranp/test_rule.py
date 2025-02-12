from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.ast import TupleTree
from rogw.tranp.implements.syntax.tranp.rule import Comps, Pattern, Roles, RuleMap, Rules
from rogw.tranp.implements.syntax.tranp.rules import python_rules
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


class TestRuleMap(TestCase):
	@data_provider([
		('python', {
			'symbols': {
				'entry': ['expr', '"\n"'],
				'expr': ['calc_sum'],
				'calc_sum': ['calc_mul', 'op_add'],
				'calc_mul': ['calc_unary', 'op_mul'],
				'calc_unary': ['op_unary', 'primary'],
				'op_add': ['/[-+]/'],
				'op_mul': ['/[*\\/%]/'],
				'op_unary': ['/[-+]/'],
				'primary': ['relay', 'atom'],
				'relay': ['primary', '"."', 'name'],
				'atom': ['var', 'str'],
				'var': ['name'],
				'name': ['/[a-zA-Z_]\\w*/'],
				'str': ['/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'"\n"': [],
				'/[-+]/': [],
				'"."': [],
				'/[*\\/%]/': [],
				'/[a-zA-Z_]\\w*/': [],
				'/\\\'[^\\\']*\\\'|"[^"]*"/': [],
			},
			'effects': {
				'entry': [],
				'expr': ['entry'],
				'calc_sum': ['expr'],
				'calc_mul': ['calc_sum'],
				'calc_unary': ['calc_mul'],
				'op_add': ['calc_sum'],
				'op_mul': ['calc_mul'],
				'op_unary': ['calc_unary'],
				'primary': ['calc_unary', 'relay'],
				'relay': ['primary'],
				'atom': ['primary'],
				'var': ['atom'],
				'name': ['relay', 'var'],
				'str': ['atom'],
				'"\n"': ['entry'],
				'/[-+]/': ['op_add', 'op_unary'],
				'"."': ['relay'],
				'/[*\\/%]/': ['op_mul'],
				'/[a-zA-Z_]\\w*/': ['name'],
				'/\\\'[^\\\']*\\\'|"[^"]*"/': ['str'],
			},
			'lookup': {
				'entry': ['entry', 'expr', '"\n"', 'calc_sum', 'calc_mul', 'op_add', 'calc_unary', 'op_mul', '/[-+]/', 'op_unary', 'primary', '/[*\\/%]/', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'expr': ['expr', 'calc_sum', 'calc_mul', 'op_add', 'calc_unary', 'op_mul', '/[-+]/', 'op_unary', 'primary', '/[*\\/%]/', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'calc_sum': ['calc_sum', 'calc_mul', 'op_add', 'calc_unary', 'op_mul', '/[-+]/', 'op_unary', 'primary', '/[*\\/%]/', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'calc_mul': ['calc_mul', 'calc_unary', 'op_mul', 'op_unary', 'primary', '/[*\\/%]/', '/[-+]/', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'calc_unary': ['calc_unary', 'op_unary', 'primary', '/[-+]/', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'op_add': ['op_add', '/[-+]/'],
				'op_mul': ['op_mul', '/[*\\/%]/'],
				'op_unary': ['op_unary', '/[-+]/'],
				'primary': ['primary', 'relay', 'atom', '"."', 'name', 'var', 'str', '/[a-zA-Z_]\\w*/', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'relay': ['relay', 'primary', '"."', 'name', 'atom', '/[a-zA-Z_]\\w*/', 'var', 'str', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'atom': ['atom', 'var', 'str', 'name', '/\\\'[^\\\']*\\\'|"[^"]*"/', '/[a-zA-Z_]\\w*/'],
				'var': ['var', 'name', '/[a-zA-Z_]\\w*/'],
				'name': ['name', '/[a-zA-Z_]\\w*/'],
				'str': ['str', '/\\\'[^\\\']*\\\'|"[^"]*"/'],
				'"\n"': ['"\n"'],
				'/[-+]/': ['/[-+]/'],
				'"."': ['"."'],
				'/[*\\/%]/': ['/[*\\/%]/'],
				'/[a-zA-Z_]\\w*/': ['/[a-zA-Z_]\\w*/'],
				'/\\\'[^\\\']*\\\'|"[^"]*"/': ['/\\\'[^\\\']*\\\'|"[^"]*"/'],
			},
			'recursive': {
				'entry': [],
				'expr': [],
				'calc_sum': [],
				'calc_mul': [],
				'calc_unary': [],
				'op_add': [],
				'op_mul': [],
				'op_unary': [],
				'primary': ['relay'],
				'relay': ['primary'],
				'atom': [],
				'var': [],
				'name': [],
				'str': [],
				'"\n"': [],
				'/[-+]/': [],
				'"."': [],
				'/[*\\/%]/': [],
				'/[a-zA-Z_]\\w*/': [],
				'/\\\'[^\\\']*\\\'|"[^"]*"/': [],
			},
		}),
	])
	def test_schema(self, grammar: str, expected: dict[str, dict[str, list[str]]]) -> None:
		instance = RuleMap(python_rules())
		for name in instance.names():
			self.assertEqual(expected['symbols'][name], instance.symbols(name))
			self.assertEqual(expected['effects'][name], instance.effects(name))
			self.assertEqual(expected['lookup'][name], instance.lookup(name))
			self.assertEqual(expected['recursive'][name], instance.recursive(name))
