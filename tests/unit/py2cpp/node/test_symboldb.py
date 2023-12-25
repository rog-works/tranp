from unittest import TestCase

from py2cpp.module.modules import Modules
from py2cpp.node.symboldb import SymbolDBFactory
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		({
			# implicit module types
			'py2cpp.python.classes.int': 'py2cpp.python.classes.int',
			'py2cpp.python.classes.float': 'py2cpp.python.classes.float',
			'py2cpp.python.classes.str': 'py2cpp.python.classes.str',
			'py2cpp.python.classes.bool': 'py2cpp.python.classes.bool',
			'py2cpp.python.classes.tuple': 'py2cpp.python.classes.tuple',
			'py2cpp.python.classes.list': 'py2cpp.python.classes.list',
			'py2cpp.python.classes.dict': 'py2cpp.python.classes.dict',
			'py2cpp.python.classes.None': 'py2cpp.python.classes.None',
			'py2cpp.python.classes.Unknown': 'py2cpp.python.classes.Unknown',
			# explicit module types
			'py2cpp.cpp.directive.pragma': 'py2cpp.cpp.directive.pragma',
			'py2cpp.cpp.directive.ifdef': 'py2cpp.cpp.directive.ifdef',
			'py2cpp.cpp.directive.ifndef': 'py2cpp.cpp.directive.ifndef',
			'py2cpp.cpp.directive.endif': 'py2cpp.cpp.directive.endif',
			# implicit import types
			'__main__.int': 'py2cpp.python.classes.int',
			'__main__.float': 'py2cpp.python.classes.float',
			'__main__.str': 'py2cpp.python.classes.str',
			'__main__.bool': 'py2cpp.python.classes.bool',
			'__main__.tuple': 'py2cpp.python.classes.tuple',
			'__main__.list': 'py2cpp.python.classes.list',
			'__main__.dict': 'py2cpp.python.classes.dict',
			'__main__.None': 'py2cpp.python.classes.None',
			'__main__.Unknown': 'py2cpp.python.classes.Unknown',
			# explicit import types
			'__main__.pragma': 'py2cpp.cpp.directive.pragma',
			# entrypoint types
			'__main__.A': '__main__.A',
			'__main__.A.B': '__main__.A.B',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.A.func1': '__main__.A.func1',
			# entrypoint symbols
			'__main__.v': '__main__.int',
			'__main__.A.v': '__main__.list',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.A.func1.self': '__main__.A',
			'__main__.A.func1.b': '__main__.list',
			'__main__.A.func1.v': '__main__.bool',
			'__main__.A.B.v': '__main__.str',
		},),
	])
	def test_make_db(self, expected: dict[str, str]) -> None:
		modules = self.fixture.get(Modules)
		db = SymbolDBFactory().create(modules)
		print('\n'.join([f'{key}: {types.scope}.{types.one_of(defs.Class | defs.Function).symbol.to_string()}' for key, types in db.items()]))
		for path, types in db.items():
			self.assertEqual('ok' if path in expected else path, 'ok')
			self.assertEqual(f'{types.scope}.{types.one_of(defs.Class | defs.Function).symbol.to_string()}', expected[path])
