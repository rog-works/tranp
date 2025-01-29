from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.tokenizer import Token, TokenDefinition, TokenDomains, PyTokenizer, TokenTypes, Lexer, Tokenizer
from rogw.tranp.test.helper import data_provider


class TestTokenizer(TestCase):
	@data_provider([
		('a + 1', ['a', '+', '1']),
		('a += b', ['a', '+=', 'b']),
		('a == b', ['a', '==', 'b']),
		('a := b', ['a', ':=', 'b']),
		('a(**b)', ['a', '(', '**', 'b', ')']),
		('**a', ['**', 'a']),
		('***a', ['**', '*', 'a']),
		('if a\\\n\tand b: ...', ['if', 'a', 'and', 'b', ':', '...']),
		('def f() -> None: ...', ['def', 'f', '(', ')', '->', 'None', ':', '...']),
		(
			'\n'.join([
				'def a(arr: list[int]) -> dict[str, int]:',
				'	return {',
				'		"b": arr[0],',
				'	}',
				'	',
				'print(a([0]))',
			]),
			[
				'def', 'a', '(', 'arr', ':', 'list', '[', 'int', ']', ')', '->', 'dict', '[', 'str', ',', 'int', ']', ':', '\n',
					'\t', 'return', '{',
						'"b"', ':', 'arr', '[', '0', ']', ',',
					'}', '\n', '',
				'print', '(', 'a', '(', '[', '0', ']', ')', ')',
			],
		),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		parser = Tokenizer()
		tokens = parser.parse(source)
		self.assertEqual(expected, [token.string for token in tokens])

	@data_provider([
		('a + 1', Tokenizer.Context(), 1, (2, []), {'nest': 0, 'enclosure': 0}),
		('a\nb', Tokenizer.Context(), 1, (2, [(TokenTypes.NewLine, '\n')]), {'nest': 0, 'enclosure': 0}),
		('a\t+ 1', Tokenizer.Context(), 1, (2, []), {'nest': 0, 'enclosure': 0}),
		('a\n\tb', Tokenizer.Context(), 1, (2, [(TokenTypes.NewLine, '\n'), (TokenTypes.Indent, '\t')]), {'nest': 1, 'enclosure': 0}),
		('\ta\n\n\tb', Tokenizer.Context(nest=1), 2, (3, [(TokenTypes.NewLine, '\n\t')]), {'nest': 1, 'enclosure': 0}),
		('\ta\nb', Tokenizer.Context(nest=1), 2, (3, [(TokenTypes.NewLine, '\n'), (TokenTypes.Dedent, '')]), {'nest': 0, 'enclosure': 0}),
		('a[\nb]', Tokenizer.Context(enclosure=1), 2, (3, []), {'nest': 0, 'enclosure': 1}),
		('\ta(\nb)', Tokenizer.Context(nest=1, enclosure=1), 3, (4, []), {'nest': 1, 'enclosure': 1}),
	])
	def test_handle_white_space(self, source: str, context: Tokenizer.Context, begin: int, expected: tuple[str, list[Token]], expected_context: dict[str, int]) -> None:
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_white_space(context, tokens, begin)
		self.assertEqual(expected, actual)
		self.assertEqual(expected_context['nest'], context.nest)
		self.assertEqual(expected_context['enclosure'], context.enclosure)

	@data_provider([
		('a.b', Tokenizer.Context(), 1, (2, [(TokenTypes.Dot, '.')]), {'nest': 0, 'enclosure': 0}),
		('(a)', Tokenizer.Context(), 0, (1, [(TokenTypes.ParenL, '(')]), {'nest': 0, 'enclosure': 1}),
		('(a.b)', Tokenizer.Context(enclosure=1), 2, (3, [(TokenTypes.Dot, '.')]), {'nest': 0, 'enclosure': 1}),
		('{"a": 1}', Tokenizer.Context(enclosure=1), 5, (6, [(TokenTypes.BraceR, '}')]), {'nest': 0, 'enclosure': 0}),
		('...', Tokenizer.Context(), 0, (3, [(TokenTypes.Ellipsis, '...')]), {'nest': 0, 'enclosure': 0}),
	])
	def test_handle_symbol(self, source: str, context: Tokenizer.Context, begin: int, expected: tuple[str, list[Token]], expected_context: dict[str, int]) -> None:
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_symbol(context, tokens, begin)
		self.assertEqual(expected, actual)
		self.assertEqual(expected_context['nest'], context.nest)
		self.assertEqual(expected_context['enclosure'], context.enclosure)

	@data_provider([
		('a + 1', Tokenizer.Context(), 2, (3, [(TokenTypes.Plus, '+')]), {'nest': 0, 'enclosure': 0}),
		('a +-1', Tokenizer.Context(), 2, (3, [(TokenTypes.Plus, '+')]), {'nest': 0, 'enclosure': 0}),
		('a += 1', Tokenizer.Context(), 2, (4, [(TokenTypes.PlusEqual, '+=')]), {'nest': 0, 'enclosure': 0}),
	])
	def test_handle_operator(self, source: str, context: Tokenizer.Context, begin: int, expected: tuple[str, list[Token]], expected_context: dict[str, int]) -> None:
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_operator(context, tokens, begin)
		self.assertEqual(expected, actual)
		self.assertEqual(expected_context['nest'], context.nest)
		self.assertEqual(expected_context['enclosure'], context.enclosure)


class TestLexer(TestCase):
	@data_provider([
		('abc', ['abc']),
		('a.b("c").d', ['a', '.', 'b', '(', '"c"', ')', '.', 'd']),
		('a * 0 - True', ['a', ' ', '*', ' ', '0', ' ', '-', ' ', 'True']),
		('?a _b', ['?', 'a', ' ', '_b']),
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
		('a.b', 1, TokenDomains.Symbol),
		('a[0]', 1, TokenDomains.Symbol),
		('[:-1]', 1, TokenDomains.Symbol),
		('a()', 1, TokenDomains.Symbol),
		('{"a": 1}', 0, TokenDomains.Symbol),
		('@a', 0, TokenDomains.Symbol),
		('"abc"', 0, TokenDomains.Quote),
		("'abc'", 0, TokenDomains.Quote),
		('"""abc"""', 0, TokenDomains.Quote),
		("r'abc'", 0, TokenDomains.Quote),
		('f"abc"', 0, TokenDomains.Quote),
		('f"""abc"""', 0, TokenDomains.Quote),
		('0.0', 0, TokenDomains.Number),
		('_a.b', 0, TokenDomains.Identifier),
		('a.b0', 2, TokenDomains.Identifier),
		('a + 0', 2, TokenDomains.Operator),
		('a / 1', 2, TokenDomains.Operator),
		('a += 1', 2, TokenDomains.Operator),
	])
	def test_analyze_domain(self, source: str, begin: int, expected: TokenDomains) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.analyze_domain(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, (1, (TokenTypes.WhiteSpace, ' '))),
		('abc ', 3, (4, (TokenTypes.WhiteSpace, ' '))),
		('ab c', 2, (3, (TokenTypes.WhiteSpace, ' '))),
		('a \t\nb\nc', 1, (4, (TokenTypes.LineBreak, '\n'))),
		('\ta\n\tbc', 2, (4, (TokenTypes.LineBreak, '\n\t'))),
		(' \t\n\t', 0, (4, (TokenTypes.LineBreak, '\n\t'))),
		('\n\n\t\n', 0, (4, (TokenTypes.LineBreak, '\n'))),
		('\n\n\t ', 0, (4, (TokenTypes.LineBreak, '\n\t'))),
		('\n\n \t', 0, (4, (TokenTypes.LineBreak, '\n '))),
	])
	def test_parse_white_space(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_white_spece(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a # bc', 2, (6, (TokenTypes.Comment, '# bc'))),
		('a # bc\n', 2, (7, (TokenTypes.Comment, '# bc\n'))),
	])
	def test_parse_comment(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_comment(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('@a', 0, (1, (TokenTypes.At, '@'))),
		('a;', 1, (2, (TokenTypes.SemiColon, ';'))),
		('[:b]', 1, (2, (TokenTypes.Colon, ':'))),
		('a(b)', 1, (2, (TokenTypes.ParenL, '('))),
	])
	def test_parse_symbol(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_symbol(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('"abc"', 0, (5, (TokenTypes.String, '"abc"'))),
		("'abc'", 0, (5, (TokenTypes.String, "'abc'"))),
		('"""abc"""', 0, (9, (TokenTypes.String, '"""abc"""'))),
		("f'abc'", 0, (6, (TokenTypes.String, "f'abc'"))),
		('r"abc"', 0, (6, (TokenTypes.String, 'r"abc"'))),
		('r"""abc"""', 0, (10, (TokenTypes.String, 'r"""abc"""'))),
		# ('/abc/', 0, (5, (TokenTypes.Regexp, '/abc/'))), XXX 一旦保留
		('"a\nbc"', 0, (6, (TokenTypes.String, '"a\nbc"'))),  # FIXME 文法的にNG
	])
	def test_parse_quote(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_quote(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('1234', 0, (4, (TokenTypes.Digit, '1234'))),
		('1234.', 0, (5, (TokenTypes.Decimal, '1234.'))),
		('1.2', 0, (3, (TokenTypes.Decimal, '1.2'))),
		('1 + 23 + 4', 4, (6, (TokenTypes.Digit, '23'))),
	])
	def test_parse_number(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_number(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('abc', 0, (3, (TokenTypes.Name, 'abc'))),
		('Abc', 0, (3, (TokenTypes.Name, 'Abc'))),
		('_Abc', 0, (4, (TokenTypes.Name, '_Abc'))),
		('_A_Bc0', 0, (6, (TokenTypes.Name, '_A_Bc0'))),
		('a.b.c', 2, (3, (TokenTypes.Name, 'b'))),
		('0 + a.b()', 6, (7, (TokenTypes.Name, 'b'))),
	])
	def test_parse_identifier(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_identifier(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a = 1', 2, (3, (TokenTypes.Equal, '='))),
		('1 - 2', 2, (3, (TokenTypes.Minus, '-'))),
		('1 +-2', 2, (3, (TokenTypes.Plus, '+'))),
		('!a', 0, (1, (TokenTypes.Exclamation, '!'))),
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
