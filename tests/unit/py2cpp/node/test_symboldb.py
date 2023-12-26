from unittest import TestCase

from py2cpp.node.symboldb import SymbolDB
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
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			# entrypoint symbols
			'__main__.v': '__main__.int',
			'__main__.A.s': '__main__.str',
			'__main__.B.v': '__main__.bool',
			'__main__.B.func1.b': '__main__.list',
			'__main__.B.func1.v': '__main__.bool',
			'__main__.B.B2.v': '__main__.str',
		},),
	])
	def test_make_db(self, expected: dict[str, str]) -> None:
		db = self.fixture.get(SymbolDB)
		print('\n'.join([f"'{key}': '{row.ref_path}'," for key, row in db.items()]))
		for path, row in db.items():
			self.assertEqual('ok' if path in expected else path, 'ok')
			self.assertEqual(f'{row.ref_path}', expected[path])
