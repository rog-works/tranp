from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import ASTTree, SyntaxParser
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, grammar_tokenizer, python_rules
from rogw.tranp.implements.syntax.tranp.tokenizer import Tokenizer
from rogw.tranp.test.helper import data_provider


class TestSyntaxParser(TestCase):
	@data_provider([
		(
			'a\nb\n',
			'python',
			('entry', [
				('var', [
					('name', 'a'),
				]),
				('var', [
					('name', 'b'),
				]),
			]),
		),
		(
			'a.b().c(1, "2")\n',
			'python',
			('entry', [
				('invoke', [
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
					('args', [
						('int', '1'),
						('str', '"2"'),
					]),
				]),
			]),
		),
		(
			'{}\n'.format('\n'.join([
				'entry := exp',
				'exp := primary',
				'primary := relay | invoke | indexer | atom',
				'relay := primary "." name',
				'invoke := primary "(" [args] ")"',
				'indexer := primary "[" expr "]"',
				'args := expr (expr)*',
			])),
			'grammar',
			('entry', [
				('rule', [('symbol', 'entry'), ('symbol', 'exp')]),
				('rule', [('symbol', 'exp'), ('symbol', 'primary')]),
				('rule', [
					('symbol', 'primary'),
					('?terms_or', [
						('symbol', 'relay'),
						('symbol', 'invoke'),
						('symbol', 'indexer'),
						('symbol', 'atom'),
					]),
				]),
				('rule', [
					('symbol', 'relay'),
					('?terms', [
						('symbol', 'primary'),
						('string', '"."'),
						('symbol', 'name'),
					]),
				]),
				('rule', [
					('symbol', 'invoke'),
					('?terms', [
						('symbol', 'primary'),
						('string', '"("'),
						('symbol', 'args'),
						('string', '")"'),
					]),
				]),
				('rule', [
					('symbol', 'indexer'),
					('?terms', [
						('symbol', 'primary'),
						('string', '"["'),
						('symbol', 'expr'),
						('string', '"]"'),
					]),
				]),
				('rule', [
					('symbol', 'args'),
					('?terms', [
						('symbol', 'expr'),
						('symbol', 'expr'),
					]),
				]),
			]),
		),
	])
	def test_parse(self, source: str, lang: str, expected: ASTTree) -> None:
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
			print(f'AST unmatch. actual: {actual.pretty}')
			raise
