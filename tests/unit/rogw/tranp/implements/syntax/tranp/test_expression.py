from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionSymbol, ExpressionTerminal, ExpressionsAnd, ExpressionsOr, ExpressionsRepeat
from rogw.tranp.implements.syntax.tranp.rule import Operators, Pattern, Patterns, Repeators
from rogw.tranp.implements.syntax.tranp.state import Context, ExpressionStore, State, States, Trigger, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestExpressionTerminal(TestCase):
	@data_provider([
		('"\n"', 0, 0, Token(TokenTypes.NewLine, '\n'), Triggers.FinishStep),
		('"\n"', 0, 0, Token(TokenTypes.Name, 'a'), Triggers.Abort),
		('"\n"', 1, 0, Token(TokenTypes.Name, 'a'), Triggers.Empty),
		(r'/[a-zA-Z_]\w*/', 0, 0, Token(TokenTypes.Name, 'a'), Triggers.FinishStep),
		(r'/[a-zA-Z_]\w*/', 0, 0, Token(TokenTypes.Digit, '0'), Triggers.Abort),
		(r'/[a-zA-Z_]\w*/', 1, 0, Token(TokenTypes.Name, 'a'), Triggers.Empty),
	])
	def test_step(self, expression: str, cursor: int, token_no: int, token: Token, expected: Trigger) -> None:
		instance = ExpressionTerminal(Pattern.make(expression))
		actual = instance.step(Context.make(cursor, {}), token_no, token)
		self.assertEqual(expected, actual)


class TestExpressionSymbol(TestCase):
	@data_provider([
		('a', 0, 0, {'a': States.Idle}, Triggers.Empty),
		('a', 0, 0, {'a': States.Step}, Triggers.Empty),
		('a', 0, 0, {'a': States.FinishSkip}, Triggers.FinishSkip),
		('a', 0, 0, {'a': States.FinishStep}, Triggers.FinishStep),
		('a', 0, 0, {'a': States.UnfinishSkip}, Triggers.UnfinishSkip),
		('a', 0, 0, {'a': States.UnfinishStep}, Triggers.UnfinishStep),
		('a', 0, 0, {'a': States.Abort}, Triggers.Abort),
		('a', 1, 0, {'a': States.Idle}, Triggers.Empty),
		('a', 1, 0, {'a': States.Step}, Triggers.Empty),
		('a', 1, 0, {'a': States.FinishStep}, Triggers.Empty),
		('a', 1, 0, {'a': States.Abort}, Triggers.Empty),
	])
	def test_accept(self, symbol: str, cursor: int, token_no: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		instance = Expression.factory(Pattern.make(symbol))
		actual = instance.accept(Context.make(cursor, {}), token_no, state_of)
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
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.FinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.FinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Abort}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.Idle}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.Step}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.FinishSkip}, Triggers.FinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.FinishSkip, States.Idle), 0, 1, {'b': States.Abort}, Triggers.FinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 0, 1, {'b': States.Abort}, Triggers.FinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.Idle}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.Step}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.FinishSkip}, Triggers.FinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishSkip, States.Idle), 0, 1, {'b': States.Abort}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 0, 1, {'b': States.Abort}, Triggers.UnfinishSkip),
		# XXX 同じ文字数で片側だけ先に確定する状況は本来あり得ないが、正しい状況を再現するのが手間なことと、検証したい状況と実質的にほぼ同等であるため一旦これで良しとする
	])
	def test_accept(self, expressions: list[str], expr_stores: list[ExpressionStore], cursor: int, token_no: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		datum = Context.Datum()
		datum.expr_stores = expr_stores
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions], op=Operators.Or))
		actual = instance.accept(Context.make(cursor, {instance: datum}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsOr)
		self.assertEqual(expected, actual)


class TestExpressionsAnd(TestCase):
	@data_provider([
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.FinishStep}, Triggers.Step),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.UnfinishSkip}, Triggers.Skip),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.UnfinishStep}, Triggers.Step),
		(['a', 'b'], build_expr_stores(States.Idle, States.Idle), 0, 0, {'a': States.Abort}, Triggers.Abort),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.Idle}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.Step}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.FinishSkip}, Triggers.FinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.FinishStep}, Triggers.FinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.FinishStep, States.Idle), 1, 1, {'b': States.Abort}, Triggers.Abort),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.Idle}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.Step}, Triggers.Empty),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.FinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.FinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.UnfinishSkip}, Triggers.UnfinishSkip),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.UnfinishStep}, Triggers.UnfinishStep),
		(['a', 'b'], build_expr_stores(States.UnfinishStep, States.Idle), 1, 1, {'b': States.Abort}, Triggers.Abort),
	])
	def test_accept(self, expressions: list[str], expr_stores: list[ExpressionStore], cursor: int, token_no: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		datum = Context.Datum()
		datum.expr_stores = expr_stores
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions]))
		actual = instance.accept(Context.make(cursor, {instance: datum}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsAnd)
		self.assertEqual(expected, actual)


class TestExpressionsRepeat(TestCase):
	@data_provider([
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Abort}, Triggers.Abort),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.FinishSkip}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.FinishStep}, Triggers.FinishStep),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.FinishSkip}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.FinishStep}, Triggers.FinishStep),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OverOne, build_expr_stores(States.FinishStep), 0, 1, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverOne, build_expr_stores(States.FinishStep), 0, 1, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverOne, build_expr_stores(States.FinishStep), 0, 1, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, build_expr_stores(States.FinishStep), 0, 1, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverOne, build_expr_stores(States.FinishStep), 0, 1, {'a': States.Abort}, Triggers.FinishSkip),
	])
	def test_accept(self, expressions: list[str], rep: Repeators, expr_stores: list[ExpressionStore], cursor: int, token_no: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		datum = Context.Datum()
		datum.expr_stores = expr_stores
		instance = Expression.factory(Patterns([Patterns([Pattern.make(expression) for expression in expressions])], rep=rep))
		actual = instance.accept(Context.make(cursor, {instance: datum}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsRepeat)
		self.assertEqual(expected, actual)
