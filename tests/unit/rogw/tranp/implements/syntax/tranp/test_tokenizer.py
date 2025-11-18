from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.token import SpecialSymbols
from rogw.tranp.implements.syntax.tranp.tokenizer import Lexer, PyTokenizer, Token, TokenDefinition, TokenDomains, Tokenizer, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestTokenizer(TestCase):
	@data_provider([
		('a + 1', ['a', '+', '1', '\n']),
		('a += b', ['a', '+=', 'b', '\n']),
		('a == b', ['a', '==', 'b', '\n']),
		('a := b', ['a', ':=', 'b', '\n']),
		('a(**b)', ['a', '(', '**', 'b', ')', '\n']),
		('**a', ['**', 'a', '\n']),
		('***a', ['**', '*', 'a', '\n']),
		('a # bc', ['a', '\n']),
		('if a\n\tand b: ...', ['if', 'a', '\n', SpecialSymbols.Indent.value, 'and', 'b', ':', '...', '\n', SpecialSymbols.Dedent.value]),
		('def f() -> None: ...', ['def', 'f', '(', ')', '->', 'None', ':', '...', '\n']),
		(
			'\n'.join([
				'# c',
				'def a(arr: list[int]) -> dict[str, int]:',
				'	# c',
				'	if arr:',
				'		return {',
				'			# c',
				'			"b": arr[0],',
				'			# c',
				'		}',
				'		# c',
				'	else:',
				'		return {}',
				'# c',
			]),
			[
				'def', 'a', '(', 'arr', ':', 'list', '[', 'int', ']', ')', '->', 'dict', '[', 'str', ',', 'int', ']', ':', '\n',
					SpecialSymbols.Indent.value, 'if', 'arr', ':', '\n',
						SpecialSymbols.Indent.value, 'return', '{',
							'"b"', ':', 'arr', '[', '0', ']', ',',
						'}', '\n',
					SpecialSymbols.Dedent.value, 'else', ':', '\n',
						SpecialSymbols.Indent.value, 'return', '{', '}', '\n',
				SpecialSymbols.Dedent.value, SpecialSymbols.Dedent.value,
			],
		),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		parser = Tokenizer()
		tokens = parser.parse(source)
		self.assertEqual(expected, [token.string for token in tokens])

	@data_provider([
		('a\nb', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.NewLine, '\n')])),
		('a\n\tb', 1, {'nest': 0, 'enclosure': 0}, {'nest': 1, 'enclosure': 0}, (2, [(TokenTypes.NewLine, '\n'), (TokenTypes.Indent, SpecialSymbols.Indent.value)])),
		('\ta\n\n\tb', 1, {'nest': 1, 'enclosure': 0}, {'nest': 1, 'enclosure': 0}, (2, [(TokenTypes.NewLine, '\n')])),
		('\ta\nb', 1, {'nest': 1, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.NewLine, '\n'), (TokenTypes.Dedent, SpecialSymbols.Dedent.value)])),
		('a[\nb]', 2, {'nest': 0, 'enclosure': 1}, {'nest': 0, 'enclosure': 1}, (3, [])),
		('\ta(\nb)', 2, {'nest': 1, 'enclosure': 1}, {'nest': 1, 'enclosure': 1}, (3, [])),
	])
	def test_handle_white_space(self, source: str, begin: int, before_context: dict[str, int], expected_context: dict[str, int], expected: tuple[str, list[Token]]) -> None:
		context = Tokenizer.Context.make(**before_context)
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_white_space(context, tokens, begin)
		self.assertEqual(expected, actual)
		self.assertEqual(expected_context, {'nest': context.nest, 'enclosure': context.enclosure})

	@data_provider([
		('a.b', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.Dot, '.')])),
		('(a)', 0, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 1}, (1, [(TokenTypes.ParenL, '(')])),
		('(a.b)', 2, {'nest': 0, 'enclosure': 1}, {'nest': 0, 'enclosure': 1}, (3, [(TokenTypes.Dot, '.')])),
		('{"a": 1}', 4, {'nest': 0, 'enclosure': 1}, {'nest': 0, 'enclosure': 0}, (5, [(TokenTypes.BraceR, '}')])),
		('...', 0, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (1, [(TokenTypes.Ellipsis, '...')])),
		('a + 1', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.Plus, '+')])),
		('a + -1', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.Plus, '+')])),
		('a += 1', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.PlusEqual, '+=')])),
		('a - -1', 2, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (3, [(TokenTypes.Minus, SpecialSymbols.OpUnaryMinus.value)])),
		('a -= -1', 1, {'nest': 0, 'enclosure': 0}, {'nest': 0, 'enclosure': 0}, (2, [(TokenTypes.MinusEqual, '-=')])),
	])
	def test_handle_symbol(self, source: str, begin: int, before_context: dict[str, int], expected_context: dict[str, int], expected: tuple[str, list[Token]]) -> None:
		context = Tokenizer.Context.make(**before_context)
		parser = Tokenizer()
		tokens = parser.lex_parse(source)
		actual = parser.handle_symbol(context, tokens, begin)
		self.assertEqual(expected, actual)
		self.assertEqual(expected_context, {'nest': context.nest, 'enclosure': context.enclosure})


class TestLexer(TestCase):
	@data_provider([
		('abc', ['abc', SpecialSymbols.EOF.value]),
		('a.b("c").d', ['a', '.', 'b', '(', '"c"', ')', '.', 'd', SpecialSymbols.EOF.value]),
		('a * 0 - True', ['a', '*', '0', '-', 'True', SpecialSymbols.EOF.value]),
		('?a _b', ['?', 'a', '_b', SpecialSymbols.EOF.value]),
		("r + r'abc'", ['r', '+', "r'abc'", SpecialSymbols.EOF.value]),
	])
	def test_parse(self, source: str, expected: list[str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse(source)
		self.assertEqual(expected, [token.string for token in actual])

	@data_provider([
		('a# c\nb# c', [(TokenTypes.Name, 'a'), (TokenTypes.LineBreak, '\n'), (TokenTypes.Name, 'b')]),
		('# c\na\n# c\nb\n# c', [(TokenTypes.Name, 'a'), (TokenTypes.LineBreak, '\n\n'), (TokenTypes.Name, 'b')]),
		('a + b', [(TokenTypes.Name, 'a'), (TokenTypes.Plus, '+'), (TokenTypes.Name, 'b')]),
		('a \nand b', [(TokenTypes.Name, 'a'), (TokenTypes.LineBreak, ' \n'), (TokenTypes.Name, 'and'), (TokenTypes.Name, 'b')]),
		(' \na\nb\n', [(TokenTypes.Name, 'a'), (TokenTypes.LineBreak, '\n'), (TokenTypes.Name, 'b')]),
	])
	def test_post_filter(self, source: str, expected: list[Token]) -> None:
		parser = Lexer(TokenDefinition())
		tokens = parser.parse_impl(source)
		actual = parser.post_filter(tokens)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, TokenDomains.WhiteSpace),
		('a\tbc', 1, TokenDomains.WhiteSpace),
		('a\tb\n', 3, TokenDomains.WhiteSpace),
		('a # bc', 2, TokenDomains.Comment),
		('"abc"', 0, TokenDomains.Quote),
		("'abc'", 0, TokenDomains.Quote),
		('"""abc"""', 0, TokenDomains.Quote),
		("r'abc'", 0, TokenDomains.Quote),
		('f"abc"', 0, TokenDomains.Quote),
		('f"""abc"""', 0, TokenDomains.Quote),
		('0.0', 0, TokenDomains.Number),
		('_a.b', 0, TokenDomains.Identifier),
		('a.b0', 2, TokenDomains.Identifier),
		('a.b', 1, TokenDomains.Symbol),
		('a[0]', 1, TokenDomains.Symbol),
		('[:-1]', 1, TokenDomains.Symbol),
		('a()', 1, TokenDomains.Symbol),
		('{"a": 1}', 0, TokenDomains.Symbol),
		('@a', 0, TokenDomains.Symbol),
		('a + 0', 2, TokenDomains.Symbol),
		('a / 1', 2, TokenDomains.Symbol),
		('a += 1', 2, TokenDomains.Symbol),
	])
	def test_analyze_domain(self, source: str, begin: int, expected: TokenDomains) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.analyze_domain(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		(' abc', 0, (1, (TokenTypes.WhiteSpace, ' '))),
		('abc ', 3, (4, (TokenTypes.WhiteSpace, ' '))),
		('ab c', 2, (3, (TokenTypes.WhiteSpace, ' '))),
		('[ab,\n\tc]', 5, (6, (TokenTypes.WhiteSpace, '\t'))),
		('a \t\nb\nc', 1, (4, (TokenTypes.LineBreak, ' \t\n'))),
		('\ta\n\tbc', 2, (4, (TokenTypes.LineBreak, '\n\t'))),
		(' \t\n\t', 0, (4, (TokenTypes.LineBreak, ' \t\n\t'))),
		('\n\n \t', 0, (4, (TokenTypes.LineBreak, '\n\n \t'))),
	])
	def test_parse_white_space(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_white_spece(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('a # bc', 2, (6, (TokenTypes.Comment, '# bc'))),
		('a # bc\n', 2, (6, (TokenTypes.Comment, '# bc'))),
	])
	def test_parse_comment(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
		actual = parser.parse_comment(source, begin)
		self.assertEqual(expected, actual)

	@data_provider([
		('"abc"', 0, (5, (TokenTypes.String, '"abc"'))),
		("'abc'", 0, (5, (TokenTypes.String, "'abc'"))),
		('"""abc"""', 0, (9, (TokenTypes.String, '"""abc"""'))),
		("f'abc'", 0, (6, (TokenTypes.String, "f'abc'"))),
		('r"abc"', 0, (6, (TokenTypes.String, 'r"abc"'))),
		('r"""abc"""', 0, (10, (TokenTypes.String, 'r"""abc"""'))),
		('\\"abc\\"', 0, (7, (TokenTypes.String, '\\"abc\\"'))),
		('"\\"a\\" \\"b\\"" c', 0, (13, (TokenTypes.String, '"\\"a\\" \\"b\\""'))),
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
		('@a', 0, (1, (TokenTypes.At, '@'))),
		('a;', 1, (2, (TokenTypes.SemiColon, ';'))),
		('[:b]', 1, (2, (TokenTypes.Colon, ':'))),
		('a(b)', 1, (2, (TokenTypes.ParenL, '('))),
		('a = 1', 2, (3, (TokenTypes.Equal, '='))),
		('1 - 2', 2, (3, (TokenTypes.Minus, '-'))),
		('1 +-2', 2, (3, (TokenTypes.Plus, '+'))),
		('!a', 0, (1, (TokenTypes.Exclamation, '!'))),
	])
	def test_parse_symbol(self, source: str, begin: int, expected: tuple[int, str]) -> None:
		parser = Lexer(TokenDefinition())
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
