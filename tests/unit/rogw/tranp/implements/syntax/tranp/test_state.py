from typing import Any
from unittest import TestCase

from rogw.tranp.implements.syntax.tranp.state import DoneReasons, State, StateMachine, States, Trigger, Triggers
from rogw.tranp.test.helper import data_provider


class TestDoneReasons(TestCase):
	@data_provider([
		(DoneReasons.Empty, {'physically': False, 'finish': False, 'unfinish': False}),
		(DoneReasons.Skip, {'physically': False, 'finish': False, 'unfinish': False}),
		(DoneReasons.Step, {'physically': True, 'finish': False, 'unfinish': False}),
		(DoneReasons.FinishSkip, {'physically': False, 'finish': True, 'unfinish': False}),
		(DoneReasons.FinishStep, {'physically': True, 'finish': True, 'unfinish': False}),
		(DoneReasons.UnfinishSkip, {'physically': False, 'finish': False, 'unfinish': True}),
		(DoneReasons.UnfinishStep, {'physically': True, 'finish': False, 'unfinish': True}),
		(DoneReasons.Abort, {'physically': False, 'finish': False, 'unfinish': False}),
	])
	def test_schema(self, reason: DoneReasons, expected: dict[str, bool]) -> None:
		self.assertEqual(expected['physically'], reason.physically)
		self.assertEqual(expected['finish'], reason.finish)
		self.assertEqual(expected['unfinish'], reason.unfinish)


class TestTrigger(TestCase):
	@data_provider([
		(Triggers.Empty, {'trigger': Trigger.Triggers.Empty, 'reason': DoneReasons.Empty, 'equal': Triggers.Empty}),
		(Triggers.Ready, {'trigger': Trigger.Triggers.Ready, 'reason': DoneReasons.Empty, 'equal': Triggers.Ready}),
		(Triggers.Skip, {'trigger': Trigger.Triggers.Skip, 'reason': DoneReasons.Skip, 'equal': Triggers.Skip}),
		(Triggers.Step, {'trigger': Trigger.Triggers.Step, 'reason': DoneReasons.Step, 'equal': Triggers.Step}),
		(Triggers.Done, {'trigger': Trigger.Triggers.Done, 'reason': DoneReasons.Empty, 'equal': Triggers.Done}),
		(Triggers.Abort, {'trigger': Trigger.Triggers.Abort, 'reason': DoneReasons.Abort, 'equal': Triggers.Abort}),
		(Triggers.FinishSkip, {'trigger': Trigger.Triggers.Done, 'reason': DoneReasons.FinishSkip, 'equal': Triggers.Done}),
		(Triggers.FinishStep, {'trigger': Trigger.Triggers.Done, 'reason': DoneReasons.FinishStep, 'equal': Triggers.Done}),
		(Triggers.UnfinishSkip, {'trigger': Trigger.Triggers.Done, 'reason': DoneReasons.UnfinishSkip, 'equal': Triggers.Done}),
		(Triggers.UnfinishStep, {'trigger': Trigger.Triggers.Done, 'reason': DoneReasons.UnfinishStep, 'equal': Triggers.Done}),
	])
	def test_schema(self, trigger: Trigger, expected: dict[str, Any]) -> None:
		self.assertEqual(expected['trigger'], trigger.trigger)
		self.assertEqual(expected['reason'], trigger.reason)
		self.assertEqual(expected['equal'], trigger)


class TestState(TestCase):
	@data_provider([
		(States.Sleep, {'state': State.States.Sleep, 'reason': DoneReasons.Empty, 'equal': States.Sleep}),
		(States.Idle, {'state': State.States.Idle, 'reason': DoneReasons.Empty, 'equal': States.Idle}),
		(States.Step, {'state': State.States.Step, 'reason': DoneReasons.Step, 'equal': States.Step}),
		(States.Done, {'state': State.States.Done, 'reason': DoneReasons.Empty, 'equal': States.Done}),
		(States.FinishSkip, {'state': State.States.Done, 'reason': DoneReasons.FinishSkip, 'equal': States.Done}),
		(States.FinishStep, {'state': State.States.Done, 'reason': DoneReasons.FinishStep, 'equal': States.Done}),
		(States.UnfinishSkip, {'state': State.States.Done, 'reason': DoneReasons.UnfinishSkip, 'equal': States.Done}),
		(States.UnfinishStep, {'state': State.States.Done, 'reason': DoneReasons.UnfinishStep, 'equal': States.Done}),
		(States.Abort, {'state': State.States.Done, 'reason': DoneReasons.Abort, 'equal': States.Done}),
	])
	def test_schema(self, state: State, expected: dict[str, Any]) -> None:
		self.assertEqual(expected['state'], state.state)
		self.assertEqual(expected['reason'], state.reason)
		self.assertEqual(expected['equal'], state)

	@data_provider([
		(Triggers.Empty, States.Idle),
		(Triggers.Ready, States.Idle),
		(Triggers.Skip, States.Idle),
		(Triggers.Step, States.Step),
		(Triggers.Done, States.Done),
		(Triggers.Abort, States.Done),
	])
	def test_from_trigger(self, trigger: Trigger, expected: State) -> None:
		self.assertEqual(States.from_trigger(trigger), expected)


class TestStateMachine(TestCase):
	def build_states(self, initial: State) -> StateMachine:
		return StateMachine(initial, {
			(Triggers.Ready, States.Sleep): States.Idle,
			(Triggers.Step, States.Idle): States.Step,
			(Triggers.Done, States.Idle): States.Done,
			(Triggers.Abort, States.Idle): States.Done,
			(Triggers.Ready, States.Step): States.Idle,
			(Triggers.Ready, States.Done): States.Idle,
		})

	@data_provider([
		(Triggers.Ready, States.Sleep, States.Idle),
		(Triggers.Skip, States.Idle, States.Idle),
		(Triggers.Step, States.Idle, States.Step),
		(Triggers.FinishSkip, States.Idle, States.Done),
		(Triggers.FinishStep, States.Idle, States.Done),
		(Triggers.UnfinishSkip, States.Idle, States.Done),
		(Triggers.UnfinishStep, States.Idle, States.Done),
		(Triggers.Abort, States.Idle, States.Done),
		(Triggers.Ready, States.Step, States.Idle),
		(Triggers.Ready, States.Done, States.Idle),
	])
	def notify(self, trigger: Trigger, initial: State, expected: State) -> None:
		instance = self.build_states(initial)
		state = States.from_trigger(trigger)
		instance.notify(trigger, {state: state})
		self.assertEqual(instance.state, expected)
