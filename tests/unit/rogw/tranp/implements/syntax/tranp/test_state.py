from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.state import States, StateMachine, States, Triggers, Triggers
from rogw.tranp.test.helper import data_provider


class TestStateMachine(TestCase):
	def build_states(self, initial: States) -> StateMachine:
		return StateMachine(initial, {
			(Triggers.Ready, States.Sleep): States.Idle,
			(Triggers.Step, States.Idle): States.Step,
			(Triggers.Done, States.Idle): States.Done,
			(Triggers.Abort, States.Idle): States.Abort,
			(Triggers.Ready, States.Step): States.Idle,
			(Triggers.Ready, States.Done): States.Idle,
			(Triggers.Ready, States.Abort): States.Idle,
		})

	@data_provider([
		(Triggers.Ready, States.Sleep, States.Idle),
		(Triggers.Skip, States.Idle, States.Idle),
		(Triggers.Step, States.Idle, States.Step),
		(Triggers.Done, States.Idle, States.Done),
		(Triggers.Abort, States.Idle, States.Abort),
		(Triggers.Ready, States.Step, States.Idle),
		(Triggers.Ready, States.Done, States.Idle),
		(Triggers.Ready, States.Abort, States.Idle),
	])
	def test_notify(self, trigger: Triggers, initial: States, expected: States) -> None:
		instance = self.build_states(initial)
		instance.notify(trigger)
		self.assertEqual(instance.state, expected)
