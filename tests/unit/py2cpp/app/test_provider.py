from unittest import TestCase

from py2cpp.lang.di import DI
from py2cpp.providers.app import di_container


class TestProvider(TestCase):
	def test_di_container(self) -> None:
		di = di_container({})
		self.assertEqual('ok' if isinstance(di, DI) else str(di), 'ok')
