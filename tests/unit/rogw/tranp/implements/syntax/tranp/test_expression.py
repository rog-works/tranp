from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionSymbol, ExpressionTerminal, ExpressionsAnd, ExpressionsOr, ExpressionsRepeat
from rogw.tranp.implements.syntax.tranp.rule import Operators, Pattern, Patterns, Repeators
from rogw.tranp.implements.syntax.tranp.state import Context, DoneReasons, StateStore, States, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token, TokenTypes
from rogw.tranp.test.helper import data_provider


class TestExpressionTerminal(TestCase):
	@data_provider([
		('"\n"', 0, 0, Token(TokenTypes.NewLine, '\n'), (Triggers.Done, DoneReasons.FinishStep)),
		('"\n"', 0, 0, Token(TokenTypes.Name, 'a'), (Triggers.Abort, DoneReasons.Empty)),
		('"\n"', 1, 0, Token(TokenTypes.Name, 'a'), (Triggers.Empty, DoneReasons.Empty)),
		(r'/[a-zA-Z_]\w*/', 0, 0, Token(TokenTypes.Name, 'a'), (Triggers.Done, DoneReasons.FinishStep)),
		(r'/[a-zA-Z_]\w*/', 0, 0, Token(TokenTypes.Digit, '0'), (Triggers.Abort, DoneReasons.Empty)),
		(r'/[a-zA-Z_]\w*/', 1, 0, Token(TokenTypes.Name, 'a'), (Triggers.Empty, DoneReasons.Empty)),
	])
	def test_step(self, expression: str, cursor: int, token_no: int, token: Token, expected: tuple[Triggers, DoneReasons]) -> None:
		instance = ExpressionTerminal(Pattern.make(expression))
		actual = instance.step(Context.make(cursor, {}), token_no, token)
		self.assertEqual(expected, actual)


class TestExpressionSymbol(TestCase):
	@data_provider([
		('a', 0, 0, {'a': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 0, 0, {'a': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 0, 0, {'a': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Done, DoneReasons.FinishSkip)),
		('a', 0, 0, {'a': (States.Done, DoneReasons.FinishStep)}, (Triggers.Done, DoneReasons.FinishStep)),
		('a', 0, 0, {'a': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 0, 0, {'a': (States.Step, DoneReasons.MatchStep)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 0, 0, {'a': (States.Abort, DoneReasons.Empty)}, (Triggers.Abort, DoneReasons.Empty)),
		('a', 1, 0, {'a': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 1, 0, {'a': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 1, 0, {'a': (States.Done, DoneReasons.FinishStep)}, (Triggers.Empty, DoneReasons.Empty)),
		('a', 1, 0, {'a': (States.Abort, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
	])
	def test_accept(self, symbol: str, cursor: int, token_no: int, on_states: dict[str, tuple[States, DoneReasons]], expected: tuple[Triggers, DoneReasons]) -> None:
		def state_of(name: str, state: States, reason: DoneReasons) -> bool:
			return name in on_states and (state, reason) == on_states[name]

		instance = Expression.factory(Pattern.make(symbol))
		actual = instance.accept(Context.make(cursor, {}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionSymbol)
		self.assertEqual(expected, actual)


def build_state_stores(*states: tuple[Triggers, DoneReasons]) -> list[StateStore]:
	state_stores: list[StateStore] = []
	for index, state in enumerate(states):
		trigger, reason = state
		if state == Triggers.Empty:
			state_stores.append(StateStore())
		else:
			state_stores.append(StateStore(trigger, reason, index, index))

	return state_stores


def empty() -> tuple[Triggers, DoneReasons]:
	return (Triggers.Empty, DoneReasons.Empty)


class TestExpressionsOr(TestCase):
	@data_provider([
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Skip, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Done, DoneReasons.FinishStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Skip, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Abort, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Idle, DoneReasons.Empty)}, (Triggers.Skip, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.Empty)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Done, DoneReasons.FinishSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Done, DoneReasons.FinishStep)}, (Triggers.Done, DoneReasons.FinishStep)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishSkip), empty()), 0, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Done, DoneReasons.FinishSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 0, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Done, DoneReasons.FinishSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Idle, DoneReasons.Empty)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.Empty)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Done, DoneReasons.FinishSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Done, DoneReasons.FinishStep)}, (Triggers.Done, DoneReasons.FinishStep)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchSkip), empty()), 0, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 0, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Step, DoneReasons.MatchSkip)),
		# XXX 同じ文字数で片側だけ先に確定する状況は本来あり得ないが、正しい状況を再現するのが手間なことと、検証したい状況と実質的にほぼ同等であるため一旦これで良しとする
	])
	def test_accept(self, expressions: list[str], state_stores: list[StateStore], cursor: int, token_no: int, on_states: dict[str, tuple[States, DoneReasons]], expected: tuple[Triggers, DoneReasons]) -> None:
		def state_of(name: str, state: States, reason: DoneReasons) -> bool:
			return name in on_states and (state, reason) == on_states[name]

		store = Context.StoreEntry()
		store.state_stores = state_stores
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions], op=Operators.Or))
		actual = instance.accept(Context.make(cursor, {instance: store}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsOr)
		self.assertEqual(expected, actual)


class TestExpressionsAnd(TestCase):
	@data_provider([
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Skip, DoneReasons.Skip)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Done, DoneReasons.FinishStep)}, (Triggers.Step, DoneReasons.Step)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Skip, DoneReasons.Skip)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.Step)),
		(['a', 'b'], build_state_stores((Triggers.Empty, DoneReasons.Empty), empty()), 0, 0, {'a': (States.Abort, DoneReasons.Empty)}, (Triggers.Abort, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Done, DoneReasons.FinishSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Done, DoneReasons.FinishStep)}, (Triggers.Done, DoneReasons.FinishStep)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Done, DoneReasons.FinishStep), empty()), 1, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Abort, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Idle, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.Empty)}, (Triggers.Empty, DoneReasons.Empty)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Done, DoneReasons.FinishSkip)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Done, DoneReasons.FinishStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.MatchSkip)}, (Triggers.Step, DoneReasons.MatchSkip)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Step, DoneReasons.MatchStep)}, (Triggers.Step, DoneReasons.MatchStep)),
		(['a', 'b'], build_state_stores((Triggers.Step, DoneReasons.MatchStep), empty()), 1, 1, {'b': (States.Abort, DoneReasons.Empty)}, (Triggers.Abort, DoneReasons.Empty)),
	])
	def test_accept(self, expressions: list[str], state_stores: list[StateStore], cursor: int, token_no: int, on_states: dict[str, tuple[States, DoneReasons]], expected: tuple[Triggers, DoneReasons]) -> None:
		def state_of(name: str, state: States, reason: DoneReasons) -> bool:
			return name in on_states and (state, reason) == on_states[name]

		store = Context.StoreEntry()
		store.state_stores = state_stores
		instance = Expression.factory(Patterns([Pattern.make(expression) for expression in expressions]))
		actual = instance.accept(Context.make(cursor, {instance: store}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsAnd)
		self.assertEqual(expected, actual)


class TestExpressionsRepeat(TestCase):
	@data_provider([
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.MatchSkip}, Triggers.Skip),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.MatchStep}, Triggers.Step),
		(['a'], Repeators.OverZero, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.MatchSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.MatchStep}, Triggers.Step),
		(['a'], Repeators.OverOne, [], 0, 0, {'a': States.Abort}, Triggers.Abort),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.FinishSkip}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.FinishStep}, Triggers.FinishStep),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.MatchSkip}, Triggers.Skip),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.MatchStep}, Triggers.Step),
		(['a'], Repeators.OneOrZero, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.FinishSkip}, Triggers.FinishSkip),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.FinishStep}, Triggers.FinishStep),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.MatchSkip}, Triggers.Skip),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.MatchStep}, Triggers.Step),
		(['a'], Repeators.OneOrEmpty, [], 0, 0, {'a': States.Abort}, Triggers.FinishSkip),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.Idle}, Triggers.Empty),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.Step}, Triggers.Empty),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.FinishSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.FinishStep}, Triggers.Step),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.MatchSkip}, Triggers.Skip),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.MatchStep}, Triggers.Step),
		(['a'], Repeators.OverOne, build_state_stores(States.FinishStep), 0, 1, {'a': States.Abort}, Triggers.FinishSkip),
	])
	def test_accept(self, expressions: list[str], rep: Repeators, state_stores: list[StateStore], cursor: int, token_no: int, on_states: dict[str, State], expected: Trigger) -> None:
		def state_of(name: str, state: State) -> bool:
			return name in on_states and state == on_states[name]

		store = Context.StoreEntry()
		store.state_stores = state_stores
		instance = Expression.factory(Patterns([Patterns([Pattern.make(expression) for expression in expressions])], rep=rep))
		actual = instance.accept(Context.make(cursor, {instance: store}), token_no, state_of)
		self.assertEqual(type(instance), ExpressionsRepeat)
		self.assertEqual(expected, actual)
