from unittest import TestCase

from py2cpp.module.modules import Modules
from py2cpp.node.classify import make_db
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestClassify(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		({
			'py2cpp.cpp.directive.pragma': 'py2cpp.cpp.directive.pragma',
			'__main__.v': 'py2cpp.python.classes.int',
			'__main__.A': '__main__.A',
			'__main__.A.v': 'py2cpp.python.classes.list',
			'__main__.A.B': '__main__.A.B',
			'__main__.A.B.v': 'py2cpp.python.classes.str',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.A.func1': '__main__.A.func1',
			'__main__.A.func1.self': '__main__.A',
			'__main__.A.func1.b': 'py2cpp.python.classes.list',
			'__main__.A.func1.v': 'py2cpp.python.classes.bool',
		},),
	])
	def test_make_db(self, expected: dict[str, str]) -> None:
		modules = self.fixture.get(Modules)
		db = make_db(modules)
		for path, types in db.items():
			self.assertEqual('ok' if path in expected else path, 'ok')
			self.assertEqual(f'{types.scope}.{types.one_of(defs.Class | defs.Function).symbol.to_string()}', expected[path])
