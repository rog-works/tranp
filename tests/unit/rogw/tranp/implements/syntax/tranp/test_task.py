from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.expression import Expression
from rogw.tranp.implements.syntax.tranp.rule import Pattern
from rogw.tranp.implements.syntax.tranp.rules import python_rules
from rogw.tranp.implements.syntax.tranp.state import States, Triggers
from rogw.tranp.implements.syntax.tranp.task import Task, Tasks
from rogw.tranp.test.helper import data_provider


class TestTask(TestCase):
	def test_usage(self) -> None:
		instance = Task('task', Expression.factory(Pattern.make('a')))
		fixtures = [
			(Triggers.Ready, States.Idle, False),
			(Triggers.Skip, States.Idle, False),
			(Triggers.Step, States.Step, False),
			(Triggers.Ready, States.Idle, False),
			(Triggers.FinishStep, States.Done, True),
			(Triggers.Ready, States.Idle, False),
			(Triggers.Abort, States.Done, False),
		]
		self.assertTrue(instance.state_of(States.Sleep))
		for trigger, state, finished in fixtures:
			instance.notify(trigger)
			self.assertTrue(instance.state_of(state))
			self.assertTrue(instance.finished == finished)

		self.assertTrue(instance.clone().state_of(States.Sleep))


class TestTasks(TestCase):
	@data_provider([
		('entry', 'primary', [('primary', 'relay')]),
		('entry', 'relay', []),
	])
	def test_recursive_from(self, base: str, via_name: str, expected: list[tuple[str, str]]) -> None:
		tasks = Tasks.from_rules(python_rules())
		self.assertEqual(tasks.recursive_from(base, [via_name]), expected)
