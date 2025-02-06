from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.syntax import ErrorCollector, SyntaxParser
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, grammar_tokenizer, python_rules
from rogw.tranp.implements.syntax.tranp.tokenizer import Tokenizer
from rogw.tranp.test.helper import data_provider


class TestSyntaxParser(TestCase):
	@data_provider([
		(
			'a.b().c + -1 == d("a" in b).e[0]',
			'python',
			('entry', [
				('comp', [
					('calc_sum', [
						('relay', [
							('invoke', [
								('relay', [
									('var', [
										('name', 'a'),
									]),
									('name', 'b'),
								]),
								('__empty__', ''),
							]),
							('name', 'c'),
						]),
						('op_add', '+'),
						('calc_unary', [
							('op_unary', '-'),
							('int', '1'),
						]),
					]),
					('op_comp', [
						('op_comp_s', '=='),
					]),
					('indexer', [
						('relay', [
							('invoke', [
								('var', [
									('name', 'd'),
								]),
								('args', [
									('comp', [
										('str', '"a"'),
										('op_comp', [
											('op_in', 'in'),
										]),
										('var', [
											('name', 'b'),
										]),
									]),
								]),
							]),
							('name', 'e'),
						]),
						('int', '0'),
					]),
				]),
			]),
		),
		(
			'\n'.join([
				'entry := exp',
				'exp[1] := atom',
				'atom[1] := relay | invoke | indexer | atom',
				'relay := atom "." name',
				'invoke := atom "(" [args] ")"',
				'indexer := atom "[" exp "]"',
				'args := exp (exp)*',
				'bool := /False|True/'
			]),
			'grammar',
			('entry', [
				('rule', [
					('symbol', 'entry'),
					('__empty__', ''),
					('symbol', 'exp'),
				]),
				('rule', [
					('symbol', 'exp'),
					('unwrap', '1'),
					('symbol', 'atom'),
				]),
				('rule', [
					('symbol', 'atom'),
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
						('symbol', 'atom'),
						('string', '"."'),
						('symbol', 'name'),
					]),
				]),
				('rule', [
					('symbol', 'invoke'),
					('__empty__', ''),
					('terms', [
						('symbol', 'atom'),
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
						('symbol', 'atom'),
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
				('rule', [
					('symbol', 'bool'),
					('__empty__', ''),
					('regexp', '/False|True/'),
				]),
			]),
		),
	])
	def test_parse(self, source: str, lang: str, expected: tuple) -> None:
		rule_provider = {
			'python': python_rules,
			'grammar': grammar_rules,
		}
		tokenizer_provider = {
			'python': Tokenizer,
			'grammar': grammar_tokenizer,
		}
		rules = rule_provider[lang]()
		tokenizer = tokenizer_provider[lang]()
		actual = SyntaxParser(rules, tokenizer).parse(source, 'entry')

		try:
			self.assertEqual(expected, actual.simplify())
		except AssertionError:
			print(f'AST unmatch. actual: {actual.pretty()}')
			raise


class TestErrorCollector(TestCase):
	@data_provider([
		# XXX 末尾に空行があり、0ステップ(=EOF)でエラーになると表示が不自然になる
		(
			'\n'.join([
				'a.b.c',
				'',
			]),
			5,
			'\n'.join([
				"pass: 5/6, token: '\\n'",
				'(0) >>> ',
				'        ^',
			]),
		),
		(
			'\n'.join([
				'a.b.c',
				'',
			]),
			1,
			'\n'.join([
				"pass: 1/6, token: '.'",
				'(1) >>> a.b.c',
				'         ^',
			]),
		),
	])
	def test_summary(self, source: str, steps: int, expected: str) -> None:
		tokens = Tokenizer().parse(source)
		actual = ErrorCollector(source, tokens, steps).summary()
		self.assertEqual(expected, actual)
