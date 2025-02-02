from collections.abc import Callable
from typing import cast
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.token import Token, TokenDomains, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestToken(TestCase):
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
		(Token(TokenTypes.LineBreak, '"\n"'), '<Token[LineBreak]: \'"\\n"\'>'),
	])
	def test_repr(self, token: Token, expected: str) -> None:
		actual = token.__repr__()
		self.assertEqual(expected, actual)

	@data_provider([
		(Token.new_line.__name__, (TokenTypes.NewLine, '\n')),
		(Token.indent.__name__, (TokenTypes.Indent, '\\INDENT')),
		(Token.dedent.__name__, (TokenTypes.Dedent, '\\DEDENT')),
		(Token.EOF.__name__, (TokenTypes.EOF, '\\EOF')),
		(Token.empty.__name__, (TokenTypes.Empty, '')),
	])
	def test_factory(self, name: str, expected: tuple[str, str]) -> None:
		actual = cast(Callable[[], Token], getattr(Token, name))()
		self.assertEqual(expected, actual)
