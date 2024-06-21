from unittest import TestCase

from rogw.tranp.app.app import App
from rogw.tranp.lang.di import DI
from rogw.tranp.lang.locator import Locator


class TestApp(TestCase):
	def test_run(self) -> None:
		class Result:
			def __str__(self) -> str:
				return 'ok'

		def task() -> Result:
			return Result()

		app = App({})
		self.assertEqual('ok', str(app.run(task)))

	def test_resolve(self) -> None:
		actual = App({}).resolve(Locator)
		self.assertEqual('ok', 'ok' if isinstance(actual, DI) else str(actual))
