from typing import cast
from unittest import TestCase

from py2cpp.app.config import default_definitions
from py2cpp.lang.module import load_module_path


class TestConfig(TestCase):
	def test_default_definitions(self) -> None:
		for symbol, injector in default_definitions().items():
			self.assertEqual(type(symbol), str)
			self.assertEqual(type(injector), str)
			load_module_path(symbol)
			load_module_path(cast(str, injector))
