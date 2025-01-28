from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.tokenizer import TokenParser, TokenParser2
from rogw.tranp.test.helper import data_provider


class TestTokenParser2(TestCase):
	@data_provider([
		('1234', 0, (4, '1234')),
		('1234.', 0, (5, '1234.')),
		('1.2', 0, (3, '1.2')),
		('1 + 23 + 4', 4, (6, '23')),
	])
	def test_parse_number(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		parser.parse_number(source, begin)


class TestTokenParser(TestCase):
	@data_provider([
		('a.b.c', ['a', '.', 'b', '.', 'c']),
		('?a _b', ['?', 'a', '_b']),
		('a := b', ['a', ':=', 'b']),
		('a += b', ['a', '+=', 'b']),
		('**a', ['**', 'a']),
		('***a', ['**', '*', 'a']),
		("r'[a-zA-Z_][0-9a-zA-Z_]*'", ["r'[a-zA-Z_][0-9a-zA-Z_]*'"]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		actual = TokenParser().parse(source)
		self.assertEqual(expected, [token for token in actual])
