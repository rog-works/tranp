from unittest import TestCase

from py2cpp.node.symboldb import SymbolDB
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)
	__verbose = False

	@data_provider([
		({
			# 標準ライブラリー(Types)
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.float': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.float',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.tuple': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.tuple',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.dict': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.dict',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.super': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.super',
			# インポートモジュール/標準ライブラリー(Types)
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.int': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.float': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.float',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.str': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.bool': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.tuple': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.tuple',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.list': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.dict': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.dict',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.None': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Unknown': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.super': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.super',
			# インポートモジュール(Types)
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.X': 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.X',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Y': 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Y',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Z': 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Z',
			# インポートモジュール(Symbols)
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.X.nx': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Y.ny': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Y.x': 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.X',
			'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Z.nz': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			# エントリーポイント/標準ライブラリー(Types)
			'__main__.int': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'__main__.float': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.float',
			'__main__.str': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str',
			'__main__.bool': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool',
			'__main__.tuple': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.tuple',
			'__main__.list': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list',
			'__main__.dict': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.dict',
			'__main__.None': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None',
			'__main__.Unknown': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown',
			'__main__.super': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.super',
			# エントリーポイント/インポートモジュール(Types)
			'__main__.Z': 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Z',
			# エントリーポイント(Types)
			'__main__.A': '__main__.A',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			# エントリーポイント(Symbols)
			'__main__.v': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int',
			'__main__.A.s': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.B.v': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list',
			'__main__.B.__init__.self': '__main__.B',
			'__main__.B.func1.self': '__main__.B',
			'__main__.B.func1.b': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list',
			'__main__.B.func1.v': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown',
			'__main__.B.B2.v': 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str',
		},),
	])
	def test_make_db(self, expected: dict[str, str]) -> None:
		db = self.fixture.get(SymbolDB)

		if self.__verbose:
			print('\n', '\n'.join([f"'{key}': '{row.org_path}'," for key, row in db.items()]))

		for expected_path, expected_org_path in expected.items():
			self.assertEqual('ok' if expected_path in db else expected_path, 'ok')
			self.assertEqual(db[expected_path].org_path, expected_org_path)

		self.assertEqual(len(db), len(expected))
