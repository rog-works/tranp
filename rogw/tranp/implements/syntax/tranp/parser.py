from collections.abc import Iterator
from enum import Enum
import re
from typing import NamedTuple, override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
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

	def done(self) -> None:
		self.notify(Triggers.Done)

	def notify(self, trigger: Triggers) -> None:
		self._process(trigger)

	def _process(self, trigger: Triggers) -> None:
		key = (trigger, self.state)
		if key in self.transisions:
			self.state = self.transisions[key]


class Context(NamedTuple):
	steps: int
	rep: Repeators


class Expression:
	def __init__(self, pattern: PatternEntry) -> None:
		self._pattern = pattern

	def watches(self, context: Context) -> list[str]:
		assert False, 'Not implemented'

	def step(self, context: Context, token: Token) -> Triggers:
		assert False, 'Not implemented'

	def accept(self, context: Context, names: list[str]) -> Triggers:
		assert False, 'Not implemented'

	@classmethod
	def factory(cls, pattern: PatternEntry) -> 'Expression':
		if isinstance(pattern, Pattern):
			if pattern.role == Roles.Terminal:
				return ExpressionTerminal(pattern)
			else:
				return ExpressionSymbol(pattern)
		if pattern.rep != Repeators.NoRepeat:
			return ExpressionsRepeat(pattern)
		elif pattern.op != Operators.Or:
			return ExpressionsOr(pattern)
		else:
			return ExpressionsAnd(pattern)


class Expressions(Expression):
	def __init__(self, patterns: Patterns) -> None:
		super().__init__(patterns)
		self._exprs = [Expression.factory(pattern) for pattern in patterns]


class ExpressionTerminal(Expression):
	@property
	def _pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		if context.steps != 0:
			return Triggers.Hold

		pattern = self._pattern
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
	def _pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return [self._pattern.expression] if context.steps == 0 else []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return Triggers.Hold

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		if context.steps != 0:
			return Triggers.Hold
		elif self._pattern.expression in names:
			return Triggers.Done
		else:
			return Triggers.Aboat


class ExpressionsOr(Expressions):
	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for expr in self._exprs:
			symbols.extend(expr.watches(context))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._select_trigger([expr.step(context, token) for expr in self._exprs])

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		return self._select_trigger([expr.accept(context, names) for expr in self._exprs])

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
		for index, expr in enumerate(self._exprs):
			symbols.extend(expr.watches(self._new_context(context, index)))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		for index, expr in enumerate(self._exprs):
			trigger = expr.step(self._new_context(context, index), token)
			if trigger != Triggers.Hold:
				return trigger

		return Triggers.Hold

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		for index, expr in enumerate(self._exprs):
			trigger = expr.accept(self._new_context(context, index), names)
			if trigger != Triggers.Hold:
				return trigger

		return Triggers.Hold

	def _new_context(self, context: Context, offset: int) -> Context:
		return Context(context.steps - offset, context.rep)


class ExpressionsRepeat(Expressions):
	def __init__(self, patterns: Patterns) -> None:
		super().__init__(patterns)
		assert len(self._exprs) == 1

	@override
	def watches(self, context: Context) -> list[str]:
		return self._exprs[0].watches(context)

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._exprs[0].step(context, token)

	@override
	def accept(self, context: Context, names: list[str]) -> Triggers:
		return self._exprs[0].accept(context, names)


class Task:
	@classmethod
	def factory(cls, name: str, pattern: PatternEntry) -> 'Task':
		if isinstance(pattern, Pattern):
			return TaskSymbol(name, pattern)
		else:
			return TaskExpression(name, pattern)

	def __init__(self, name: str) -> None:
		self._name = name
		self._steps = 0
		self._states = StateMachine(States.Ready, {
			(Triggers.Lookup, States.Ready): States.Idle,
			(Triggers.Done, States.Idle): States.Finish,
			(Triggers.Aboat, States.Idle): States.Ready,
			(Triggers.Lookup, States.Finish): States.Idle,
			(Triggers.Done, States.Finish): States.Ready,
		})

	@property
	def name(self) -> str:
		return self._name

	def stat_in(self, *expects: States) -> bool:
		return self._states.state in expects

	def notify(self, trigger: Triggers) -> None:
		if trigger == Triggers.Lookup:
			self._steps = 0
		elif trigger == Triggers.Step:
			self._steps += 1
		elif trigger == Triggers.Done:
			self._steps = 0
		elif trigger == Triggers.Aboat:
			self._steps = 0

		self._states.notify(trigger)

	def lookup(self, on: bool) -> None:
		self.notify(Triggers.Lookup if on else Triggers.Done)

	def watches(self) -> list[str]:
		assert False, 'Not implemented'

	def step(self, token: Token) -> None:
		assert False, 'Not implemented'

	def accept(self, names: list[str]) -> None:
		assert False, 'Not implemented'


class TaskSymbol(Task):
	def __init__(self, name: str, pattern: PatternEntry) -> None:
		super().__init__(name)
		self._expr = Expression.factory(pattern)
		self._context = Context(0, Repeators.NoRepeat)

	@override
	def watches(self) -> list[str]:
		return self._expr.watches(self._context)

	@override
	def step(self, token: Token) -> None:
		self.notify(self._expr.step(self._context, token))

	@override
	def accept(self, names: list[str]) -> None:
		self.notify(self._expr.accept(self._context, names))


class TaskExpression(Task):
	def __init__(self, name: str, pattern: PatternEntry) -> None:
		super().__init__(name)
		self._exprs = Expression.factory(pattern)

	def _new_context(self) -> Context:
		return Context(self._steps, Repeators.NoRepeat)

	@override
	def watches(self) -> list[str]:
		return self._exprs.watches(self._new_context())

	@override
	def step(self, token: Token) -> None:
		self.notify(self._exprs.step(self._new_context(), token))

	@override
	def accept(self, names: list[str]) -> None:
		self.notify(self._exprs.accept(self._new_context(), names))


class SyntaxParser:
	def __init__(self, rules: Rules) -> None:
		self.rules = rules

	def parse(self, tokens: list[Token], entrypoint: str) -> Iterator[ASTEntry]:
		return self._parse(self.new_tasks(), tokens, entrypoint)

	def new_tasks(self) -> dict[str, Task]:
		return {name: Task.factory(name, pattern) for name, pattern in self.rules.items()}

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

		return [name for name in lookup_names if tasks[name].stat_in(States.Idle)]

	def step(self, tasks: dict[str, Task], token: Token, names: list[str]) -> list[str]:
		for name in names:
			tasks[name].step(token)

		return [name for name in names if tasks[name].stat_in(States.Finish)]

	def accept(self, tasks: dict[str, Task], names: list[str], finish_names: list[str]) -> list[str]:
		new_finish_names = finish_names.copy()
		on_finish_names = new_finish_names
		while len(on_finish_names) > 0:
			accept_names = [name for name in names if tasks[name].stat_in(States.Idle)]
			for name in accept_names:
				tasks[name].accept(on_finish_names)

			on_finish_names = [name for name in accept_names if tasks[name].stat_in(States.Finish)]
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
