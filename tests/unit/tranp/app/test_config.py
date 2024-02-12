from typing import cast
from unittest import TestCase

from tranp.app.config import default_definitions
from tranp.lang.module import load_module_path


class TestConfig(TestCase):
	def test_default_definitions(self) -> None:
		for symbol, injector in default_definitions().items():
			self.assertEqual(type(symbol), str)
			self.assertEqual(type(injector), str)
			load_module_path(symbol)
			load_module_path(cast(str, injector))
