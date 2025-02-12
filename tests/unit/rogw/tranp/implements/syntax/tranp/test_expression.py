from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionSymbol, ExpressionTerminal, ExpressionsAnd
from rogw.tranp.implements.syntax.tranp.rule import Pattern, Patterns
from rogw.tranp.implements.syntax.tranp.state import Context, State, States, Trigger, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestExpressionTerminal(TestCase):
	@data_provider([
		('"\n"', 0, Token(TokenTypes.NewLine, '\n'), Triggers.FinishStep),
		('"\n"', 0, Token(TokenTypes.Name, 'a'), Triggers.Abort),
		('"\n"', 1, Token(TokenTypes.Name, 'a'), Triggers.Empty),
		(r'/[a-zA-Z_]\w*/', 0, Token(TokenTypes.Name, 'a'), Triggers.FinishStep),
		(r'/[a-zA-Z_]\w*/', 0, Token(TokenTypes.Digit, '0'), Triggers.Abort),
		(r'/[a-zA-Z_]\w*/', 1, Token(TokenTypes.Name, 'a'), Triggers.Empty),
	])
	def test_step(self, expression: str, cursor: int, token: Token, expected: Trigger) -> None:
		instance = ExpressionTerminal(Pattern.make(expression))
		actual = instance.step(Context.new(cursor, {}), 0, token)
		self.assertEqual(expected, actual)


class TestExpressionSymbol(TestCase):
	@data_provider([
		('hoge', 0, States.Idle, Triggers.Empty),
		('hoge', 0, States.Step, Triggers.Empty),
		('hoge', 0, States.FinishSkip, Triggers.FinishSkip),
		('hoge', 0, States.FinishStep, Triggers.FinishStep),
		('hoge', 0, States.UnfinishSkip, Triggers.UnfinishSkip),
		('hoge', 0, States.UnfinishStep, Triggers.UnfinishStep),
		('hoge', 0, States.Abort, Triggers.Abort),
		('hoge', 1, States.Idle, Triggers.Empty),
		('hoge', 1, States.Step, Triggers.Empty),
		('hoge', 1, States.FinishStep, Triggers.Empty),
		('hoge', 1, States.Abort, Triggers.Empty),
	])
	def test_accept(self, symbol: str, cursor: int, on_state: State, expected: Trigger) -> None:
		instance = Expression.factory(Pattern.make(symbol))
		actual = instance.accept(Context.new(cursor, {}), 0, lambda name, state: name == symbol and state == on_state)
		self.assertEqual(type(instance), ExpressionSymbol)
		self.assertEqual(expected, actual)


class TestExpressionAnd(TestCase):
	@data_provider([
		(['a', '"."', 'b'], 0, States.Idle, Triggers.Empty),
		(['a', '"."', 'b'], 0, States.Step, Triggers.Empty),
		(['a', '"."', 'b'], 0, States.FinishSkip, Triggers.Skip),
		(['a', '"."', 'b'], 0, States.FinishStep, Triggers.Step),
		(['a', '"."', 'b'], 0, States.UnfinishSkip, Triggers.Skip),
		(['a', '"."', 'b'], 0, States.UnfinishStep, Triggers.Step),
		(['a', '"."', 'b'], 0, States.Abort, Triggers.Abort),
		(['a', '"."', 'b'], 2, States.Idle, Triggers.Empty),
		(['a', '"."', 'b'], 2, States.Step, Triggers.Empty),
		(['a', '"."', 'b'], 2, States.FinishSkip, Triggers.FinishSkip),
		(['a', '"."', 'b'], 2, States.FinishStep, Triggers.FinishStep),
		(['a', '"."', 'b'], 2, States.UnfinishSkip, Triggers.UnfinishSkip),
		(['a', '"."', 'b'], 2, States.UnfinishStep, Triggers.UnfinishStep),
		(['a', '"."', 'b'], 2, States.Abort, Triggers.Abort),
	])
	def test_accept(self, expressions: list[str], cursor: int, on_state: State, expected: Trigger) -> None:
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions]))
		actual = instance.accept(Context.new(cursor, {}), 0, lambda name, state: name == expressions[cursor] and state == on_state)
		self.assertEqual(type(instance), ExpressionsAnd)
		self.assertEqual(expected, actual)
