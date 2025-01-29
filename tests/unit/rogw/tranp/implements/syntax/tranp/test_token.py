from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.token import Token, TokenDomains, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestToken(TestCase):
	@data_provider([
		(Token(TokenTypes.WhiteSpace, ''), TokenDomains.WhiteSpace),
		(Token(TokenTypes.Comment, ''), TokenDomains.Comment),
		(Token(TokenTypes.Dot, ''), TokenDomains.Symbol),
		(Token(TokenTypes.String, ''), TokenDomains.Quote),
		(Token(TokenTypes.Digit, ''), TokenDomains.Number),
		(Token(TokenTypes.Name, ''), TokenDomains.Identifier),
		(Token(TokenTypes.Less, ''), TokenDomains.Operator),
		(Token(TokenTypes.DoubleAnd, ''), TokenDomains.Operator),
		(Token.empty(), TokenDomains.Unknown),
	])
	def test_domain(self, token: Token, expected: TokenDomains) -> None:
		self.assertEqual(expected, token.domain)
