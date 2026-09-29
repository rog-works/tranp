from unittest import TestCase

from tranp.app.app.app import App
from tranp.app.lang.di import DI
from tranp.app.lang.locator import Locator


class TestApp(TestCase):
	def test_run(self) -> None:
		class Result:
			def __str__(self) -> str:
				return 'ok'

		def task() -> Result:
			return Result()

		app = App({})
		self.assertEqual(str(app.run(task)), 'ok')

	def test_resolve(self) -> None:
		actual = App({}).resolve(Locator)
		self.assertEqual('ok' if isinstance(actual, DI) else str(actual), 'ok')
