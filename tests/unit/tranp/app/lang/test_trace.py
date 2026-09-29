from collections.abc import Callable
from unittest import TestCase

from tranp.app.lang.trace import Records
from tranp.app.test.helper import data_provider


def func() -> None:
	Records.instance().put()


class TestTrace(TestCase):
	@data_provider([
		(func, {'test_trace.py': 1, 'total': 1}),
	])
	def test_usage(self, func: Callable[[], None], expected: dict[str, int]) -> None:
		func()
		for key, calls in Records.instance().summary().items():
			if key == 'total':
				self.assertEqual(calls, expected[key])
			else:
				self.assertEqual(calls, expected[key.split(':')[0]])
