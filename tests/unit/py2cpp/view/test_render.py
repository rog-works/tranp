import os
from typing import Any
from unittest import TestCase

from py2cpp.view.render import Renderer
from tests.test.helper import data_provider

class Fixture:
	@classmethod
	def appdir(cls) -> str:
		return os.path.join(os.path.dirname(__file__), '../../../..')

	@classmethod
	def view(cls) -> Renderer:
		return Renderer(os.path.join(cls.appdir(), 'example/template'))


class TestView(TestCase):
	@data_provider([
		('move_assign.j2', 0, {'symbol': 'hoge', 'value': '1234'}, 'hoge = 1234;'),
		('move_assign.j2', 2, {'symbol': 'hoge', 'value': '1234'}, '\t\thoge = 1234;'),
	])
	def test_render(self, template: str, indent: int, vars: dict[str, Any], expected: str) -> None:
		view = Fixture.view()
		actual = view.render(template, indent=indent, vars=vars)
		self.assertEqual(actual, expected)
