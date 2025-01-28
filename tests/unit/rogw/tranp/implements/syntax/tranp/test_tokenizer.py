from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.tokenizer import TokenClasses, PyTokenizer, Tokenizer
from rogw.tranp.test.helper import data_provider


class TestTokenizer(TestCase):
	@data_provider([
		('abc', ['abc']),
		('a.b("c").d', ['a', '.', 'b', '(', '"c"', ')', '.', 'd']),
		('a * 0 - True', ['a', '*', '0', '-', 'True']),
		('?a _b', ['?', 'a', '_b']),
		('a := b', ['a', ':=', 'b']),
		('a += b', ['a', '+=', 'b']),
		('**a', ['**', 'a']),
		('***a', ['**', '*', 'a']),
		("r + r'abc'", ['r', '+', "r'abc'"]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		parser = Tokenizer()
		actual = parser.parse(source)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, TokenClasses.WhiteSpace),
		('a\tbc', 1, TokenClasses.WhiteSpace),
		('a\tb\n', 3, TokenClasses.WhiteSpace),
		('a # bc', 2, TokenClasses.Comment),
		('0.0', 0, TokenClasses.Number),
		('"abc"', 0, TokenClasses.Quote),
		("'abc'", 0, TokenClasses.Quote),
		("r'abc'", 0, TokenClasses.Quote),
		('f"abc"', 0, TokenClasses.Quote),
		('_a.b', 0, TokenClasses.Identifier),
		('a.b0', 2, TokenClasses.Identifier),
		('a + 0', 2, TokenClasses.Symbol),
		('a / 1', 2, TokenClasses.Symbol),
	])
	def test_analyze_class(self, source: str, begin: int, expected: TokenClasses) -> None:
		parser = Tokenizer()
		actual = parser.analyze_class(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, (1, '')),
		('abc ', 3, (4, '')),
		('ab c', 2, (3, '')),
		('a \t\nb\nc', 1, (4, '')),
	])
	def test_parse_white_space(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Tokenizer()
		actual = parser.parse_white_spece(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a # bc', 2, (6, '# bc')),
		('a # bc\n', 2, (7, '# bc\n')),
	])
	def test_parse_comment(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Tokenizer()
		actual = parser.parse_comment(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('1234', 0, (4, '1234')),
		('1234.', 0, (5, '1234.')),
		('1.2', 0, (3, '1.2')),
		('1 + 23 + 4', 4, (6, '23')),
	])
	def test_parse_number(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Tokenizer()
		actual = parser.parse_number(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('"abc"', 0, (5, '"abc"')),
		("'abc'", 0, (5, "'abc'")),
	])
	def test_parse_quote(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Tokenizer()
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
		parser = Tokenizer()
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
		parser = Tokenizer()
		actual = parser.parse_symbol(source, begin)
		self.assertEqual(expected, actual)


class TestPyTokenizer(TestCase):
	@data_provider([
		('abc', ['abc']),
		('a.b("c").d', ['a', '.', 'b', '(', '"c"', ')', '.', 'd']),
		('a * 0 - True', ['a', '*', '0', '-', 'True']),
		('?a _b', ['?', 'a', '_b']),
		('a := b', ['a', ':=', 'b']),
		('a += b', ['a', '+=', 'b']),
		('**a', ['**', 'a']),
		('***a', ['**', '*', 'a']),
		("r + r'abc'", ['r', '+', "r'abc'"]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		actual = PyTokenizer().parse(source)
		self.assertEqual(expected, [token for token in actual])
