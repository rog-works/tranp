from unittest import TestCase

from tranp.analyze.db import SymbolDB
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		({
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Union': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Union',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Unknown': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Unknown',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.int': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.float': 'tests.unit.tranp.analyze.fixtures.test_db_classes.float',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.str': 'tests.unit.tranp.analyze.fixtures.test_db_classes.str',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.bool': 'tests.unit.tranp.analyze.fixtures.test_db_classes.bool',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.tuple': 'tests.unit.tranp.analyze.fixtures.test_db_classes.tuple',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Pair': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Pair',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.dict': 'tests.unit.tranp.analyze.fixtures.test_db_classes.dict',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.None': 'tests.unit.tranp.analyze.fixtures.test_db_classes.None',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.object': 'tests.unit.tranp.analyze.fixtures.test_db_classes.object',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.type': 'tests.unit.tranp.analyze.fixtures.test_db_classes.type',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.super': 'tests.unit.tranp.analyze.fixtures.test_db_classes.super',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.id': 'tests.unit.tranp.analyze.fixtures.test_db_classes.id',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.print': 'tests.unit.tranp.analyze.fixtures.test_db_classes.print',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.enumerate': 'tests.unit.tranp.analyze.fixtures.test_db_classes.enumerate',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.range': 'tests.unit.tranp.analyze.fixtures.test_db_classes.range',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.len': 'tests.unit.tranp.analyze.fixtures.test_db_classes.len',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.T_Seq': 'tranp.compatible.python.template.T_Seq',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.__actual__': 'tranp.compatible.python.embed.__actual__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Any': 'typing.Any',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Generic': 'typing.Generic',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Iterator': 'typing.Iterator',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Sequence': 'typing.Sequence',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.int.__init__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int.__init__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.float.__init__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.float.__init__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__init__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__init__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__iter__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__iter__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.append': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list.append',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.pop': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list.pop',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.object.__init__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.object.__init__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception.__init__': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception.__init__',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.int.__init__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.int.__init__.value': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Union',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.float.__init__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.float',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.float.__init__.value': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Union',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__init__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__init__.iterable': 'typing.Iterator',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.__iter__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.append.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.append.elem': 'tranp.compatible.python.template.T_Seq',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.pop.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.list.pop.index': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.object.__init__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.object',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception.__init__.self': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception.__init__.args': 'typing.Any',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.id.instance': 'typing.Any',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.print.args': 'typing.Any',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.enumerate.iterable': 'typing.Sequence',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.range.size': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_classes.len.iterable': 'typing.Sequence',
			'tranp.compatible.python.template.TypeVar': 'typing.TypeVar',
			'tranp.compatible.python.template.T_Seq': 'tranp.compatible.python.template.T_Seq',
			'tranp.compatible.python.embed.Callable': 'typing.Callable',
			'tranp.compatible.python.embed.TypeVar': 'typing.TypeVar',
			'tranp.compatible.python.embed.T': 'tranp.compatible.python.embed.T',
			'tranp.compatible.python.embed.__actual__': 'tranp.compatible.python.embed.__actual__',
			'tranp.compatible.python.embed.__actual__.decorator': 'tranp.compatible.python.embed.__actual__.decorator',
			'tranp.compatible.python.embed.__alias__': 'tranp.compatible.python.embed.__alias__',
			'tranp.compatible.python.embed.__alias__.decorator': 'tranp.compatible.python.embed.__alias__.decorator',
			'tranp.compatible.python.embed.__actual__.name': 'tests.unit.tranp.analyze.fixtures.test_db_classes.str',
			'tranp.compatible.python.embed.__actual__.decorator.wrapped': 'tranp.compatible.python.embed.T',
			'tranp.compatible.python.embed.__alias__.name': 'tests.unit.tranp.analyze.fixtures.test_db_classes.str',
			'tranp.compatible.python.embed.__alias__.decorator.wrapped': 'tranp.compatible.python.embed.T',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.X': 'tests.unit.tranp.analyze.fixtures.test_db_xyz.X',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.Y': 'tests.unit.tranp.analyze.fixtures.test_db_xyz.Y',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.Z': 'tests.unit.tranp.analyze.fixtures.test_db_xyz.Z',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.X.nx': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.Y.ny': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.Y.x': 'tests.unit.tranp.analyze.fixtures.test_db_xyz.X',
			'tests.unit.tranp.analyze.fixtures.test_db_xyz.Z.nz': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'typing.Any': 'typing.Any',
			'typing.Callable': 'typing.Callable',
			'typing.Generic': 'typing.Generic',
			'typing.Sequence': 'typing.Sequence',
			'typing.TypeAlias': 'typing.TypeAlias',
			'typing.TypeVar': 'typing.TypeVar',
			'typing.T_Seq': 'typing.T_Seq',
			'typing.Iterator': 'typing.Iterator',
			'typing.Iterator.__next__': 'typing.Iterator.__next__',
			'typing.Iterator.__next__.self': 'typing.Iterator',
			'__main__.Z': 'tests.unit.tranp.analyze.fixtures.test_db_xyz.Z',
			'__main__.TypeAlias': 'typing.TypeAlias',
			'__main__.DSI': '__main__.DSI',
			'__main__.A': '__main__.A',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.B2.class_func': '__main__.B.B2.class_func',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			'__main__.B.func2': '__main__.B.func2',
			'__main__.B.func2.closure': '__main__.B.func2.closure',
			'__main__.v': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'__main__.d': '__main__.DSI',
			'__main__.A.s': 'tests.unit.tranp.analyze.fixtures.test_db_classes.str',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.B.v': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'__main__.B.B2.v': 'tests.unit.tranp.analyze.fixtures.test_db_classes.str',
			'__main__.B.B2.class_func.cls': '__main__.B.B2',
			'__main__.B.__init__.self': '__main__.B',
			'__main__.B.func1.self': '__main__.B',
			'__main__.B.func1.b': 'tests.unit.tranp.analyze.fixtures.test_db_classes.list',
			'__main__.B.func1.v': 'tests.unit.tranp.analyze.fixtures.test_db_classes.bool',
			'__main__.B.func2.self': '__main__.B',
			'__main__.B.func2.for.i': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
			'__main__.B.func2.try.e': 'tests.unit.tranp.analyze.fixtures.test_db_classes.Exception',
			'__main__.B.func2.closure.a': 'tests.unit.tranp.analyze.fixtures.test_db_classes.int',
		},),
	])
	def test___init__(self, expected: dict[str, str]) -> None:
		db = self.fixture.get(SymbolDB)

		try:
			for expected_path, expected_org_path in expected.items():
				self.assertEqual('ok' if expected_path in db.raws else expected_path, 'ok')
				self.assertEqual(db.raws[expected_path].org_path, expected_org_path)

			for key, value in db.raws.items():
				self.assertEqual('ok' if key in expected else key, 'ok')

			self.assertEqual(len(db.raws), len(expected))
		except AssertionError as e:
			print('\n', '\n'.join([f"'{key}': '{raw.org_path}'," for key, raw in db.raws.items()]))
			raise
