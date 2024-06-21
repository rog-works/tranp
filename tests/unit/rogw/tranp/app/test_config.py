from typing import cast
from unittest import TestCase

from rogw.tranp.app.config import default_definitions
from rogw.tranp.lang.module import load_module_path


class TestConfig(TestCase):
	def test_default_definitions(self) -> None:
		for symbol, injector in default_definitions().items():
			self.assertEqual(str, type(symbol))
			self.assertEqual(str, type(injector))
			load_module_path(symbol)
			load_module_path(cast(str, injector))
