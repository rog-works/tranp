from typing import Any, Callable
from unittest import TestCase

from rogw.tranp.lang.defer import Difer
from rogw.tranp.test.helper import data_provider


class A:
	def func(self) -> int:
		return 1


class TestDifer(TestCase):
	@data_provider([
		(lambda: A(), {
			'class': A,
			'invoke': (A.func.__name__, 1),
			'eq': False,
			'ne': True,
		}),
		(lambda: 'abc', {
			'class': str,
			'invoke': (str.split.__name__, ['abc']),
			'str': 'abc',
			'len': 3,
			'eq': True,
			'ne': False,
			'add': ('d', 'abcd'),
			'getitem': (slice(1, 3), 'bc'),
		}),
	])
	def test_usage(self, factory: Callable[[], Any], expected: dict[str, Any]) -> None:
		instance = Difer.new(factory)
		invoker: Callable[[], Any] = getattr(instance, expected['invoke'][0])
		self.assertEqual(instance.__class__, expected['class'])
		self.assertEqual(invoker(), expected['invoke'][1])
		self.assertEqual(instance == factory(), expected['eq'])
		self.assertEqual(instance != factory(), expected['ne'])
		if 'str' in expected:
			self.assertEqual(str(instance), expected['str'])
		if 'len' in expected:
			self.assertEqual(len(instance), expected['len'])
		if 'add' in expected:
			self.assertEqual(instance + expected['add'][0], expected['add'][1])
		if 'getitem' in expected:
			self.assertEqual(instance[expected['getitem'][0]], expected['getitem'][1])
