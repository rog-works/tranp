from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.parser import ASTTree, SyntaxParser, TokenParser
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, python_rules
from rogw.tranp.test.helper import data_provider


class TestTokenParser(TestCase):
	@data_provider([
		('a.b.c', ['a', '.', 'b', '.', 'c']),
		('?a _b', ['?', 'a', '_b']),
		('a := b', ['a', ':=', 'b']),
		("r'[a-zA-Z_][0-9a-zA-Z_]*'", ["r'[a-zA-Z_][0-9a-zA-Z_]*'"]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		actual = TokenParser.parse(source)
		self.assertEqual(expected, [token.string for token in actual])


class TestSyntaxParser(TestCase):
	@data_provider([
		(
			'a.b.c',
			'python',
			('entry', [
				('relay', [
					('relay', [
						('var', [
							('name', 'a'),
						]),
						('name', 'b'),
					]),
					('name', 'c'),
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
								('name', 'a'),
							]),
							('name', 'b'),
						]),
						('args', [
							('str', '"c"'),
						]),
					]),
					('name', 'd'),
				])
			]),
		),
		(
			'a := d\n',
			'grammar',
			('entry', [
				('rule', [
					('symbol', 'a'),
					('symbol', 'b'),
				])
			]),
		),
	])
	def test_parse(self, source: str, lang: str, expected: ASTTree) -> None:
		rule_provider = {
			'python': python_rules,
			'grammar': grammar_rules,
		}
		rules = rule_provider[lang]()
		actual = SyntaxParser(rules).parse(source, 'entry')

		try:
			self.assertEqual(expected, actual)
		except AssertionError:
			print(f'AST unmatch. actual: {actual}')
			raise
