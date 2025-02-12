from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionSymbol, ExpressionTerminal, ExpressionsAnd, ExpressionsOr
from rogw.tranp.implements.syntax.tranp.rule import Operators, Pattern, Patterns
from rogw.tranp.implements.syntax.tranp.state import Context, ExpressionStore, State, States, Trigger, Triggers
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
		actual = instance.step(Context.make(cursor, {}), 0, token)
		self.assertEqual(expected, actual)


class TestExpressionSymbol(TestCase):
	@data_provider([
		('hoge', 0, {'hoge': States.Idle}, Triggers.Empty),
		('hoge', 0, {'hoge': States.Step}, Triggers.Empty),
		('hoge', 0, {'hoge': States.FinishSkip}, Triggers.FinishSkip),
		('hoge', 0, {'hoge': States.FinishStep}, Triggers.FinishStep),
		('hoge', 0, {'hoge': States.UnfinishSkip}, Triggers.UnfinishSkip),
		('hoge', 0, {'hoge': States.UnfinishStep}, Triggers.UnfinishStep),
		('hoge', 0, {'hoge': States.Abort}, Triggers.Abort),
		('hoge', 1, {'hoge': States.Idle}, Triggers.Empty),
		('hoge', 1, {'hoge': States.Step}, Triggers.Empty),
		('hoge', 1, {'hoge': States.FinishStep}, Triggers.Empty),
		('hoge', 1, {'hoge': States.Abort}, Triggers.Empty),
	])
	def test_accept(self, symbol: str, cursor: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		instance = Expression.factory(Pattern.make(symbol))
		actual = instance.accept(Context.make(cursor, {}), 0, state_of)
		self.assertEqual(type(instance), ExpressionSymbol)
		self.assertEqual(expected, actual)


def build_expr_stores(*states: State) -> list[ExpressionStore]:
	expr_stores: list[ExpressionStore] = []
	for index, state in enumerate(states):
		if state == States.Idle:
			expr_stores.append(ExpressionStore())
		else:
			expr_stores.append(ExpressionStore(state, index, index))

	return expr_stores


class TestExpressionsOr(TestCase):
	@data_provider([
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, {}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, {'a': States.FinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, {'a': States.Abort}, Triggers.Empty),
		# XXX 同じ文字数で片側だけ先に確定する状況は本来あり得ないが、正しい状況を再現するのが手間なことと、実質的にはほぼ同等であるため一旦これで良しとする
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, {'b': States.Idle}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, {'b': States.Abort}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, {'b': States.Abort}, Triggers.UnfinishStep),
	])
	def test_accept(self, expressions: list[str], expr_stores: list[ExpressionStore], cursor: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		datum = Context.Datum()
		datum.expr_stores = expr_stores
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions], op=Operators.Or))
		actual = instance.accept(Context.make(cursor, {instance: datum}), 0, state_of)
		self.assertEqual(type(instance), ExpressionsOr)
		self.assertEqual(expected, actual)


class TestExpressionsAnd(TestCase):
	@data_provider([
		(['a', '"."', 'b'], 0, {'a': States.Idle}, Triggers.Empty),
		(['a', '"."', 'b'], 0, {'a': States.Step}, Triggers.Empty),
		(['a', '"."', 'b'], 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a', '"."', 'b'], 0, {'a': States.FinishStep}, Triggers.Step),
		(['a', '"."', 'b'], 0, {'a': States.UnfinishSkip}, Triggers.Skip),
		(['a', '"."', 'b'], 0, {'a': States.UnfinishStep}, Triggers.Step),
		(['a', '"."', 'b'], 0, {'a': States.Abort}, Triggers.Abort),
		(['a', '"."', 'b'], 2, {'b': States.Idle}, Triggers.Empty),
		(['a', '"."', 'b'], 2, {'b': States.Step}, Triggers.Empty),
		(['a', '"."', 'b'], 2, {'b': States.FinishSkip}, Triggers.FinishSkip),
		(['a', '"."', 'b'], 2, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', '"."', 'b'], 2, {'b': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', '"."', 'b'], 2, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', '"."', 'b'], 2, {'b': States.Abort}, Triggers.Abort),
	])
	def test_accept(self, expressions: list[str], cursor: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions]))
		actual = instance.accept(Context.make(cursor, {}), 0, state_of)
		self.assertEqual(type(instance), ExpressionsAnd)
		self.assertEqual(expected, actual)
