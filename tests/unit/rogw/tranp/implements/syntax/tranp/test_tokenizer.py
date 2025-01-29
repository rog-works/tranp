from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.tokenizer import Token, TokenDefinition, TokenDomains, PyTokenizer, TokenTypes, Lexer, Tokenizer
from rogw.tranp.test.helper import data_provider


class TestTokenizer(TestCase):
	@data_provider([
		('a + 1', Tokenizer.Context(), 1, (2, [])),
		('a\nb', Tokenizer.Context(), 1, (2, [Token(TokenTypes.NewLine, '\n')])),
		('a\t+ 1', Tokenizer.Context(), 1, (2, [])),
		('\ta\nb', Tokenizer.Context(nest=1), 2, (3, [Token(TokenTypes.NewLine, '\n'), Token(TokenTypes.Dedent, '')])),
		('a[\nb]', Tokenizer.Context(enclosure=1), 2, (3, [])),
		('\ta(\nb)', Tokenizer.Context(nest=1, enclosure=1), 3, (4, [])),
	])
	def test_handle_white_space(self, source: str, context: Tokenizer.Context, begin: int, expected: tuple[str, list[Token]]) -> None:
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_white_space(context, tokens, begin)
		self.assertEqual(expected, actual)


class TestLexer(TestCase):
	@data_provider([
		('abc', ['abc']),
		('a.b("c").d', ['a', '.', 'b', '(', '"c"', ')', '.', 'd']),
		('a * 0 - True', ['a', ' ', '*', ' ', '0', ' ', '-', ' ', 'True']),
		('?a _b', ['?', 'a', ' ', '_b']),
		# ('a := b', ['a', ' ', ':=', ' ', 'b']), XXX 一旦保留
		# ('a += b', ['a', ' ', '+=', ' ', 'b']),
		# ('**a', ['**', 'a']),
		# ('***a', ['**', '*', 'a']),
		("r + r'abc'", ['r', ' ', '+', ' ', "r'abc'"]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse(source)
		self.assertEqual(expected, [token.string for token in actual])

	@data_provider([
		(' abc', 0, TokenDomains.WhiteSpace),
		('a\tbc', 1, TokenDomains.WhiteSpace),
		('a\tb\n', 3, TokenDomains.WhiteSpace),
		('a # bc', 2, TokenDomains.Comment),
		('0.0', 0, TokenDomains.Number),
		('"abc"', 0, TokenDomains.Quote),
		("'abc'", 0, TokenDomains.Quote),
		('"""abc"""', 0, TokenDomains.Quote),
		("r'abc'", 0, TokenDomains.Quote),
		('f"abc"', 0, TokenDomains.Quote),
		('f"""abc"""', 0, TokenDomains.Quote),
		('_a.b', 0, TokenDomains.Identifier),
		('a.b0', 2, TokenDomains.Identifier),
		('a + 0', 2, TokenDomains.Operator),
		('a / 1', 2, TokenDomains.Operator),
		('a += 1', 2, TokenDomains.Operator),
		('a.b', 1, TokenDomains.Symbol),
		('a[0]', 1, TokenDomains.Symbol),
		('[:-1]', 1, TokenDomains.Symbol),
		('a()', 1, TokenDomains.Symbol),
		('{"a": 1}', 0, TokenDomains.Symbol),
		('@a', 0, TokenDomains.Symbol),
	])
	def test_analyze_domain(self, source: str, begin: int, expected: TokenDomains) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.analyze_domain(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, (1, Token(TokenTypes.WhiteSpace, ' '))),
		('abc ', 3, (4, Token(TokenTypes.WhiteSpace, ' '))),
		('ab c', 2, (3, Token(TokenTypes.WhiteSpace, ' '))),
		('a \t\nb\nc', 1, (4, Token(TokenTypes.WhiteSpace, ' \t\n'))),
	])
	def test_parse_white_space(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_white_spece(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a # bc', 2, (6, Token(TokenTypes.Comment, '# bc'))),
		('a # bc\n', 2, (7, Token(TokenTypes.Comment, '# bc\n'))),
	])
	def test_parse_comment(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_comment(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('@a', 0, (1, Token(TokenTypes.At, '@'))),
		('a;', 1, (2, Token(TokenTypes.SemiColon, ';'))),
		('[:b]', 1, (2, Token(TokenTypes.Colon, ':'))),
		('a(b)', 1, (2, Token(TokenTypes.ParenL, '('))),
	])
	def test_parse_symbol(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_symbol(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('"abc"', 0, (5, Token(TokenTypes.String, '"abc"'))),
		("'abc'", 0, (5, Token(TokenTypes.String, "'abc'"))),
		('"""abc"""', 0, (9, Token(TokenTypes.String, '"""abc"""'))),
		("f'abc'", 0, (6, Token(TokenTypes.String, "f'abc'"))),
		('r"abc"', 0, (6, Token(TokenTypes.String, 'r"abc"'))),
		('r"""abc"""', 0, (10, Token(TokenTypes.String, 'r"""abc"""'))),
		# ('/abc/', 0, (5, Token(TokenTypes.Regexp, '/abc/'))), XXX 一旦保留
		('"a\nbc"', 0, (6, Token(TokenTypes.String, '"a\nbc"'))),  # FIXME 文法的にNG
	])
	def test_parse_quote(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_quote(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('1234', 0, (4, Token(TokenTypes.Digit, '1234'))),
		('1234.', 0, (5, Token(TokenTypes.Decimal, '1234.'))),
		('1.2', 0, (3, Token(TokenTypes.Decimal, '1.2'))),
		('1 + 23 + 4', 4, (6, Token(TokenTypes.Digit, '23'))),
	])
	def test_parse_number(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_number(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('abc', 0, (3, Token(TokenTypes.Name, 'abc'))),
		('Abc', 0, (3, Token(TokenTypes.Name, 'Abc'))),
		('_Abc', 0, (4, Token(TokenTypes.Name, '_Abc'))),
		('_A_Bc0', 0, (6, Token(TokenTypes.Name, '_A_Bc0'))),
		('a.b.c', 2, (3, Token(TokenTypes.Name, 'b'))),
		('0 + a.b()', 6, (7, Token(TokenTypes.Name, 'b'))),
	])
	def test_parse_identifier(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_identifier(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a = 1', 2, (3, Token(TokenTypes.Equal, '='))),
		('1 - 2', 2, (3, Token(TokenTypes.Minus, '-'))),
		('1 +-2', 2, (3, Token(TokenTypes.Plus, '+'))),
		('!a', 0, (1, Token(TokenTypes.Exclamation, '!'))),
		# ('a += 1', 2, (4, Token(TokenTypes.PlusEqual, '+='))),
		# ('a == b', 2, (4, Token(TokenTypes.DoubleEqual, '=='))),
		# ('a(**b)', 2, (4, Token(TokenTypes.DoubleAster, '**'))),
		# ('def f() -> None: ...', 8, (10, Token(TokenTypes.Arrow, '->'))),
	])
	def test_parse_operator(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_operator(source, begin)
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
		(
			'\n'.join([
				'a = b',
				'	b = c',
				'',
				'	c = d',
				'd in e',
			]),
			[
				'a', '=', 'b', '\n',
				'\t',  # INDENT
					'b', '=', 'c', '\n',
					'\n',  # NL?
					'c', '=', 'd', '\n',
				'',  # DEDENT
				'd', 'in', 'e',
			]
		),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		actual = PyTokenizer().parse(source)
		self.assertEqual(expected, [token.string for token in actual])
