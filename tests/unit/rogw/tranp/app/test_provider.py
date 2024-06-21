from unittest import TestCase

from rogw.tranp.lang.di import DI
from rogw.tranp.providers.app import di_container


class TestProvider(TestCase):
	def test_di_container(self) -> None:
		di = di_container({})
		self.assertEqual('ok', 'ok' if isinstance(di, DI) else str(di))
