from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import ExpressionTerminal
from rogw.tranp.implements.syntax.tranp.rule import Pattern
from rogw.tranp.implements.syntax.tranp.state import Context, Trigger, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestExpressionTerminal(TestCase):
	@data_provider([
		(r'/\w+/', Token(TokenTypes.Name, 'a'), Triggers.FinishStep),
	])
	def test_step(self, expression: str, token: Token, expected: Trigger) -> None:
		instance = ExpressionTerminal(Pattern.make(expression))
		actual = instance.step(Context.new(0, {}), 0, token)
		self.assertEqual(expected, actual)
