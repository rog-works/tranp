from collections.abc import Callable, Iterator
from enum import Enum
import re
from typing import override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.tokenizer import ITokenizer, Tokenizer
from rogw.tranp.lang.convertion import as_a


class Triggers(Enum):
	Lookup = 0
	Hold = 1
	Step = 2
	Done = 3
	Aboat = 4


class States(Enum):
	Ready = 0
	Idle = 1
	Finish = 2


class StateMachine:
	def __init__(self, initial: States, transisions: dict[tuple[Triggers, States], States]) -> None:
		self.state = initial
		self.transisions = transisions
		self.handlers: dict[tuple[Triggers, States], Callable[[], None]] = {}

	def notify(self, trigger: Triggers) -> None:
		self._process(trigger)

	def _process(self, trigger: Triggers) -> None:
		key = (trigger, self.state)
		if key in self.transisions:
			self.state = self.transisions[key]

		if key in self.handlers:
			self.handlers[key]()

	def on(self, trigger: Triggers, state: States, callback: Callable[[], None]) -> None:
		key = (trigger, state)
		self.handlers[key] = callback

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: {self.state.name} at {hex(id(self)).upper()}>'


class Context:
	def __init__(self, cursor: int) -> None:
		self.cursor = cursor

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: #{self.cursor} at {hex(id(self)).upper()}>'


class Expression:
	@classmethod
	def factory(cls, pattern: PatternEntry) -> 'Expression':
		if isinstance(pattern, Pattern):
			if pattern.role == Roles.Terminal:
				return ExpressionTerminal(pattern)
			else:
				return ExpressionSymbol(pattern)
		else:
			if pattern.rep != Repeators.NoRepeat:
				return ExpressionsRepeat(pattern)
			elif pattern.op == Operators.Or:
				return ExpressionsOr(pattern)
			else:
				return ExpressionsAnd(pattern)

	def __init__(self, pattern: PatternEntry) -> None:
		self._pattern = pattern

	def watches(self, context: Context) -> list[str]:
		assert False, 'Not implemented'

	def step(self, context: Context, token: Token) -> Triggers:
		assert False, 'Not implemented'

	def accept(self, context: Context, names: list[str]) -> Triggers:
		assert False, 'Not implemented'

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}: with {self._pattern.__repr__()}>'


class Expressions(Expression):
	def __init__(self, pattern: PatternEntry) -> None:
		super().__init__(pattern)
		self._expressions = [Expression.factory(pattern) for pattern in as_a(Patterns, pattern)]


class ExpressionTerminal(Expression):
	@property
	def _as_pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		if context.cursor != 0:
			return Triggers.Hold

		pattern = self._as_pattern
		if pattern.comp == Comps.Regexp:
			if re.fullmatch(pattern.expression[1:-1], token.string) is not None:
				return Triggers.Done
			else:
				return Triggers.Aboat
		else:
			if pattern.expression[1:-1] == token.string:
				return Triggers.Done
			else:
				return Triggers.Aboat

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		return Triggers.Hold


class ExpressionSymbol(Expression):
	@property
	def _as_pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return [self._as_pattern.expression] if context.cursor == 0 else []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return Triggers.Hold

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		if context.cursor != 0:
			return Triggers.Hold
		elif self._as_pattern.expression in names:
			return Triggers.Done
		else:
			return Triggers.Aboat


class ExpressionsOr(Expressions):
	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for expression in self._expressions:
			symbols.extend(expression.watches(context))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._select_trigger([expression.step(context, token) for expression in self._expressions])

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		return self._select_trigger([expression.accept(context, names) for expression in self._expressions])

	def _select_trigger(self, triggers: list[Triggers]) -> Triggers:
		priorities = [Triggers.Done, Triggers.Step, Triggers.Hold]
		for expect in priorities:
			if expect in triggers:
				return expect

		return Triggers.Aboat

class ExpressionsAnd(Expressions):
	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for index, expression in enumerate(self._expressions):
			symbols.extend(expression.watches(self._new_context(context, index)))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		for index, expression in enumerate(self._expressions):
			trigger = expression.step(self._new_context(context, index), token)
			if trigger != Triggers.Hold:
				return trigger

		return Triggers.Hold

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		for index, expression in enumerate(self._expressions):
			trigger = expression.accept(self._new_context(context, index), names)
			if trigger != Triggers.Hold:
				return trigger

		return Triggers.Hold

	def _new_context(self, context: Context, offset: int) -> Context:
		return Context(context.cursor - offset)


class ExpressionsRepeat(Expressions):
	def __init__(self, pattern: PatternEntry) -> None:
		assert len(as_a(Patterns, pattern).entries) == 1
		super().__init__(pattern)
		self._repeats = 0

	@property
	def _as_patterns(self) -> Patterns:
		return as_a(Patterns, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return self._expressions[0].watches(context)

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._handle_result(self._expressions[0].step(context, token))

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		return self._handle_result(self._expressions[0].accept(context, names))

	def _handle_result(self, trigger: Triggers) -> Triggers:
		patterns = self._as_patterns
		if trigger == Triggers.Aboat:
			if patterns.rep != Repeators.OverOne:
				self._repeats = 0
				return Triggers.Done
			elif self._repeats >= 1:
				self._repeats = 0
				return Triggers.Done
		elif trigger == Triggers.Done:
			if patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				self._repeats = 0
				return Triggers.Done
			else:
				self._repeats += 1
				return Triggers.Step

		return trigger


class Task:
	def __init__(self, name: str, pattern: PatternEntry) -> None:
		self._name = name
		self._expression = Expression.factory(pattern)
		self._cursor = 0
		self._states = StateMachine(States.Ready, {
			(Triggers.Lookup, States.Ready): States.Idle,
			(Triggers.Done, States.Idle): States.Finish,
			(Triggers.Aboat, States.Idle): States.Ready,
			(Triggers.Lookup, States.Finish): States.Idle,
			(Triggers.Done, States.Finish): States.Ready,
		})
		self._states.on(Triggers.Lookup, States.Ready, lambda: self._cursor_to(0))
		self._states.on(Triggers.Lookup, States.Finish, lambda: self._cursor_to(0))
		self._states.on(Triggers.Step, States.Idle, lambda: self._cursor_add(1))

	@property
	def name(self) -> str:
		return self._name

	def state_in(self, *expects: States) -> bool:
		return self._states.state in expects

	def notify(self, trigger: Triggers) -> None:
		self._states.notify(trigger)

	def lookup(self, on: bool) -> None:
		self.notify(Triggers.Lookup if on else Triggers.Done)

	def watches(self) -> list[str]:
		return self._expression.watches(self._new_context())

	def step(self, token: Token) -> None:
		self.notify(self._expression.step(self._new_context(), token))

	def accept(self, names: list[str]) -> None:
		self.notify(self._expression.accept(self._new_context(), names))

	def _cursor_add(self, add: int) -> None:
		self._cursor += add

	def _cursor_to(self, at: int) -> None:
		self._cursor = at

	def _new_context(self) -> Context:
		return Context(self._cursor)

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}["{self.name}"]: {self._states.state.name} #{self._cursor}>'


class SyntaxParser:
	def __init__(self, rules: Rules, tokenizer: ITokenizer | None = None) -> None:
		self.rules = rules
		self.tokenizer = tokenizer if tokenizer else Tokenizer()

	def parse(self, source: str, entrypoint: str) -> Iterator[ASTEntry]:
		tokens = self.tokenizer.parse(source)
		tasks = self.new_tasks()
		return self._parse(tasks, tokens, entrypoint)

	def new_tasks(self) -> dict[str, Task]:
		return {name: Task(name, pattern) for name, pattern in self.rules.items()}

	def _parse(self, tasks: dict[str, Task], tokens: list[Token], entrypoint: str) -> Iterator[ASTEntry]:
		index = 0
		entries: list[ASTEntry] = []
		while index < len(tokens):
			names = self.lookup(tasks, entrypoint)
			finish_names = self.step(tasks, tokens[index], names)
			finish_names = self.accept(tasks, names, finish_names)
			if len(finish_names) == 0:
				continue

			index += 1
			ast, entries = self.stack(tokens[index], entries.copy(), finish_names)
			yield ast

	def lookup(self, tasks: dict[str, Task], entrypoint: str) -> list[str]:
		task = tasks[entrypoint]
		lookup_names = task.watches()
		stack_names = lookup_names.copy()
		while len(stack_names) > 0:
			name = stack_names.pop(0)
			add_names = tasks[name].watches()
			lookup_names.extend(add_names)
			stack_names.extend(add_names)

		for name, task in tasks.items():
			task.lookup(name in lookup_names)

		return [name for name in lookup_names if tasks[name].state_in(States.Idle)]

	def step(self, tasks: dict[str, Task], token: Token, names: list[str]) -> list[str]:
		for name in names:
			tasks[name].step(token)

		return [name for name in names if tasks[name].state_in(States.Finish)]

	def accept(self, tasks: dict[str, Task], names: list[str], finish_names: list[str]) -> list[str]:
		new_finish_names = finish_names.copy()
		on_finish_names = new_finish_names
		while len(on_finish_names) > 0:
			accept_names = [name for name in names if tasks[name].state_in(States.Idle)]
			for name in accept_names:
				tasks[name].accept(on_finish_names)

			on_finish_names = [name for name in accept_names if tasks[name].state_in(States.Finish)]
			new_finish_names.extend(on_finish_names)

		return new_finish_names

	def stack(self, token: Token, entries: list[ASTEntry], names: list[str]) -> tuple[ASTEntry, list[ASTEntry]]:
		ast: ASTEntry = ASTToken.empty()
		for name in names:
			if name not in self.rules:
				ast = ASTToken(token.type.name, token)
				entries.append(ast)
				continue

			pattern = self.rules[name]
			if isinstance(pattern, Pattern):
				ast = ASTToken(name, token)
				entries.append(ast)
			else:
				ast = ASTTree(name, entries)
				entries = [ast]

		return ast, entries
