from collections.abc import Callable
from typing import cast
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.token import Token, TokenDomains, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestToken(TestCase):
	@data_provider([
		(Token(TokenTypes.String, '"a"'), (TokenTypes.String, '"a"', '"a"')),
		(Token(TokenTypes.String, '"\\n"'), (TokenTypes.String, '"\\n"', '"\n"')),
		(Token(TokenTypes.LineBreak, '\n'), (TokenTypes.LineBreak, '\n', '\n')),
	])
	def test_props(self, token: Token, expected: tuple[TokenTypes, str, str]) -> None:
		self.assertEqual((token.type, token.string, token.string_of_unescaped), expected)

	@data_provider([
		(Token(TokenTypes.WhiteSpace, ''), TokenDomains.WhiteSpace),
		(Token(TokenTypes.Comment, ''), TokenDomains.Comment),
		(Token(TokenTypes.String, ''), TokenDomains.Quote),
		(Token(TokenTypes.Digit, ''), TokenDomains.Number),
		(Token(TokenTypes.Name, ''), TokenDomains.Identifier),
		(Token(TokenTypes.Dot, ''), TokenDomains.Symbol),
		(Token(TokenTypes.Less, ''), TokenDomains.Symbol),
		(Token(TokenTypes.DoubleAnd, ''), TokenDomains.Symbol),
		(Token.empty(), TokenDomains.Unknown),
	])
	def test_domain(self, token: Token, expected: TokenDomains) -> None:
		self.assertEqual(expected, token.domain)

	@data_provider([
		(Token(TokenTypes.LineBreak, '\n'), (TokenTypes.LineBreak, '\n')),
	])
	def test_simplify(self, token: Token, expected: tuple[str, str]) -> None:
		actual = token.simplify()
		self.assertEqual(expected, actual)

	@data_provider([
		(Token(TokenTypes.LineBreak, '\n'), [Token(TokenTypes.LineBreak, '\n\t')], (TokenTypes.LineBreak, '\n\n\t')),
	])
	def test_joined(self, token: Token, other: list[Token], expected: tuple[str, str]) -> None:
		actual = token.joined(*other)
		self.assertEqual(expected, actual)

	@data_provider([
		(Token(TokenTypes.LineBreak, '"\n"'), '<Token[LineBreak]: \'"\\n"\' (0, 0)..(0, 0)>'),
	])
	def test_repr(self, token: Token, expected: str) -> None:
		actual = token.__repr__()
		self.assertEqual(expected, actual)

	@data_provider([
		(Token(TokenTypes.LineBreak, '\n'), Token.to_new_line.__name__, (TokenTypes.NewLine, '\n')),
		(Token(TokenTypes.LineBreak, '\n'), Token.to_indent.__name__, (TokenTypes.Indent, '\\INDENT')),
		(Token(TokenTypes.LineBreak, '\n'), Token.to_dedent.__name__, (TokenTypes.Dedent, '\\DEDENT')),
	])
	def test_convertion(self, token: Token, name: str, expected: tuple[str, str]) -> None:
		actual = cast(Callable[[], Token], getattr(token, name))()
		self.assertEqual(expected, actual)

	@data_provider([
		(Token.EOF.__name__, (TokenTypes.EOF, '\\EOF')),
		(Token.empty.__name__, (TokenTypes.Empty, '')),
	])
	def test_factory(self, name: str, expected: tuple[str, str]) -> None:
		actual = cast(Callable[..., Token], getattr(Token, name))()
		self.assertEqual(expected, actual)


class TestSourceMap(TestCase):
	@data_provider([
		('', 0, 0, (0, 0, 0, 0)),
		('\nb', 1, 2, (1, 0, 1, 1)),
		('a\nb', 0, 1, (0, 0, 0, 1)),
		('a\nb', 1, 2, (0, 1, 1, 0)),
		('\n\n\na.bcd.e', 5, 8, (3, 2, 3, 5)),
	])
	def test_make(self, source: str, begin: int, end: int, expected: tuple[int, int, int, int]) -> None:
		actual = Token.SourceMap.make(source, begin, end)
		self.assertEqual(expected, actual)

	@data_provider([
		(Token.SourceMap.EOF.__name__, (-1, -1, -1, -1)),
		(Token.SourceMap.empty.__name__, (0, 0, 0, 0)),
	])
	def test_factory(self, name: str, expected: tuple[int, int, int, int]) -> None:
		actual = cast(Callable[..., Token.SourceMap], getattr(Token.SourceMap, name))()
		self.assertEqual(expected, actual)
