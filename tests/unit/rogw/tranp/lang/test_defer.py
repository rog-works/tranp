from collections.abc import Callable
from typing import Any
from unittest import TestCase

from rogw.tranp.lang.defer import Defer
from rogw.tranp.test.helper import data_provider


class A:
	def func(self) -> int:
		return 1


class TestDefer(TestCase):
	@data_provider([
		(lambda: A(), {'class': A, 'invoke': (A.func.__name__, 1), 'eq': False, 'ne': True}),
	])
	def test_usage(self, factory: Callable[[], Any], expected: dict[str, Any]) -> None:
		instance = Defer.new(factory)
		invoker: Callable[[], Any] = getattr(instance, expected['invoke'][0])
		self.assertEqual(Defer.resolve(instance).__class__, expected['class'])
		self.assertEqual(instance.__class__, expected['class'])
		self.assertEqual(invoker(), expected['invoke'][1])
		self.assertEqual(instance == factory(), expected['eq'])
		self.assertEqual(instance != factory(), expected['ne'])
