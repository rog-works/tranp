from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.tokenizer import TokenParser, TokenParser2
from rogw.tranp.test.helper import data_provider


class TestTokenParser2(TestCase):
	@data_provider([
		(' abc', 0, (1, ' ')),
		('abc ', 3, (4, ' ')),
		('ab c', 2, (3, ' ')),
		('a \t\nb\nc', 1, (4, ' \t\n')),
	])
	def test_parse_white_space(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_white_spece(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a # bc', 2, (6, '# bc')),
		('a # bc\n', 2, (7, '# bc\n')),
		('a """bc""" d', 2, (10, '"""bc"""')),
		('a """b\nc""" d', 2, (11, '"""b\nc"""')),
	])
	def test_parse_comment(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_comment(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('1234', 0, (4, '1234')),
		('1234.', 0, (5, '1234.')),
		('1.2', 0, (3, '1.2')),
		('1 + 23 + 4', 4, (6, '23')),
	])
	def test_parse_number(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_number(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('"abc"', 0, (5, '"abc"')),
		("'abc'", 0, (5, "'abc'")),
		('(a./abc/)', 3, (8, '/abc/')),
	])
	def test_parse_quote(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_quote(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('abc', 0, (3, 'abc')),
		('Abc', 0, (3, 'Abc')),
		('_Abc', 0, (4, '_Abc')),
		('_A_Bc0', 0, (6, '_A_Bc0')),
		('a.b.c', 2, (3, 'b')),
		('0 + a.b()', 6, (7, 'b')),
	])
	def test_parse_identifier(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_identifier(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('1 + 2', 2, (3, '+')),
		('1 +-2', 2, (3, '+')),
		('a = 1', 2, (3, '=')),
		('a += 1', 2, (4, '+=')),
		('a(**b)', 1, (2, '(')),
		('a(**b)', 2, (4, '**')),
		('a == b', 2, (4, '==')),
		('@a', 0, (1, '@')),
		('!a', 0, (1, '!')),
		('a;', 1, (2, ';')),
		('[:b]', 1, (2, ':')),
	])
	def test_parse_symbol(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = TokenParser2()
		actual = parser.parse_symbol(source, begin)
		self.assertEqual(expected, actual)


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
