from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import ASTTree, SyntaxParser
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, grammar_tokenizer, python_rules
from rogw.tranp.implements.syntax.tranp.token import TokenTypes
from rogw.tranp.implements.syntax.tranp.tokenizer import Tokenizer
from rogw.tranp.test.helper import data_provider


class TestSyntaxParser(TestCase):
	@data_provider([
		(
			'a.b.c',
			'python',
			('entry', [
				('relay', [
					('relay', [
						('var', [
							('name', (TokenTypes.Name, 'a')),
						]),
						('name', (TokenTypes.Name, 'b')),
					]),
					('name', (TokenTypes.Name, 'c')),
				]),
			]),
		),
		(
			'a.b("c").d',
			'python',
			('entry', [
				('relay', [
					('invoke', [
						('relay', [
							('var', [
								('name', (TokenTypes.Name, 'a')),
							]),
							('name', (TokenTypes.Name, 'b')),
						]),
						('args', [
							('str', (TokenTypes.String, '"c"')),
						]),
					]),
					('name', (TokenTypes.Name, 'd')),
				])
			]),
		),
		(
			''.join([
				'entry := symbol\n',
				'symbol := /[a-zA-Z_]\\w*/\n',
			]),
			'grammar',
			('entry', [
				('rule', [('symbol', (TokenTypes.Name, 'entry')), ('symbol', (TokenTypes.Name, 'symbol'))]),
				('rule', [('symbol', (TokenTypes.Name, 'symbol')), ('regexp', (TokenTypes.Regexp, '/[a-zA-Z_]\\w*/'))]),
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
			self.assertEqual(expected, actual)
		except AssertionError:
			print(f'AST unmatch. actual: {actual}')
			raise
