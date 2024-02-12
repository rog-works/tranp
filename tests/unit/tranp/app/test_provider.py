from unittest import TestCase

from tranp.lang.di import DI
from tranp.providers.app import di_container


class TestProvider(TestCase):
	def test_di_container(self) -> None:
		di = di_container({})
		self.assertEqual('ok' if isinstance(di, DI) else str(di), 'ok')
