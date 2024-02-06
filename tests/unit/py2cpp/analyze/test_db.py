from unittest import TestCase

from py2cpp.analyze.db import SymbolDB
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)
	__verbose = False

	@data_provider([
		({
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Union': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Union',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Unknown': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Unknown',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.float': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.float',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.bool': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.bool',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.tuple': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.tuple',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Pair': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Pair',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.dict': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.dict',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.type': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.type',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.super': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.super',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Exception': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Exception',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.id': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.id',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.print': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.print',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.enumerate': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.enumerate',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.range': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.range',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.len': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.len',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.T_Seq': 'py2cpp.compatible.python.template.T_Seq',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.__actual__': 'py2cpp.compatible.python.embed.__actual__',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Any': 'typing.Any',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Generic': 'typing.Generic',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Iterator': 'typing.Iterator',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Sequence': 'typing.Sequence',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__init__': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__init__',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__iter__': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__iter__',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.append': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.append',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.pop': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.pop',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__init__.self': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__init__.iterable': 'typing.Iterator',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.__iter__.self': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.append.self': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.append.elem': 'py2cpp.compatible.python.template.T_Seq',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.pop.self': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list.pop.index': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.id.instance': 'typing.Any',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.print.args': 'typing.Any',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.enumerate.iterable': 'typing.Sequence',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.range.size': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analyze.fixtures.test_db_classes.len.iterable': 'typing.Sequence',
			'py2cpp.compatible.python.template.TypeVar': 'typing.TypeVar',
			'py2cpp.compatible.python.template.T_Seq': 'py2cpp.compatible.python.template.T_Seq',
			'py2cpp.compatible.python.embed.Callable': 'typing.Callable',
			'py2cpp.compatible.python.embed.TypeVar': 'typing.TypeVar',
			'py2cpp.compatible.python.embed.T': 'py2cpp.compatible.python.embed.T',
			'py2cpp.compatible.python.embed.__actual__': 'py2cpp.compatible.python.embed.__actual__',
			'py2cpp.compatible.python.embed.__actual__.decorator': 'py2cpp.compatible.python.embed.__actual__.decorator',
			'py2cpp.compatible.python.embed.__alias__': 'py2cpp.compatible.python.embed.__alias__',
			'py2cpp.compatible.python.embed.__alias__.decorator': 'py2cpp.compatible.python.embed.__alias__.decorator',
			'py2cpp.compatible.python.embed.__actual__.name': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.embed.__actual__.decorator.wrapped': 'py2cpp.compatible.python.embed.T',
			'py2cpp.compatible.python.embed.__alias__.name': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.embed.__alias__.decorator.wrapped': 'py2cpp.compatible.python.embed.T',
			'typing.Any': 'typing.Any',
			'typing.Callable': 'typing.Callable',
			'typing.Generic': 'typing.Generic',
			'typing.Sequence': 'typing.Sequence',
			'typing.TypeVar': 'typing.TypeVar',
			'typing.T_Seq': 'typing.T_Seq',
			'typing.Iterator': 'typing.Iterator',
			'typing.Iterator.__next__': 'typing.Iterator.__next__',
			'typing.Iterator.__next__.self': 'typing.Iterator',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.X': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.X',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Y': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Y',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Z': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Z',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.X.nx': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Y.ny': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Y.x': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.X',
			'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Z.nz': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'__main__.Z': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz.Z',
			'__main__.A': '__main__.A',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.B2.class_func': '__main__.B.B2.class_func',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			'__main__.B.func2': '__main__.B.func2',
			'__main__.B.func2.closure': '__main__.B.func2.closure',
			'__main__.v': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'__main__.A.s': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.B.v': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'__main__.B.B2.v': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			'__main__.B.B2.class_func.cls': '__main__.B.B2',
			'__main__.B.__init__.self': '__main__.B',
			'__main__.B.func1.self': '__main__.B',
			'__main__.B.func1.b': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			'__main__.B.func1.v': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.bool',
			'__main__.B.func2.self': '__main__.B',
			'__main__.B.func2.for.i': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			'__main__.B.func2.try.e': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Exception',
			'__main__.B.func2.closure.a': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# エントリーポイント(FuncCall/Literal)
			# '__main__.int@25': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.A.__init__.str@64': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			# '__main__.B.B2.str@91': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			# '__main__.B.B2.class_func.Pair@126': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.Pair',
			# '__main__.B.B2.class_func.dict@125': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.dict',
			# '__main__.B.__init__.super@154': '__main__.A',
			# '__main__.B.__init__.func_call@152': '__main__.A',
			# '__main__.B.__init__.list@177': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.list',
			# '__main__.B.func1.bool@213': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.bool',
			# '__main__.B.func1.func_call@214': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None',
			# '__main__.B.func1.func_call@223': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None',
			# '__main__.B.func1.int@247': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func1.func_call@235': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None',
			# '__main__.B.func1.str@261': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.str',
			# '__main__.B.func1.int@273': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.closure.int@323': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.for.int@339': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.for.func_call@333': 'typing.Iterator',
			# '__main__.B.func2.for.func_call@342': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.None',
			# '__main__.B.func2.for.if.int@358': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.for.if.func_call@362': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.try.while.bool@372': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.bool',
			# '__main__.B.func2.try.while.if.int@381': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
			# '__main__.B.func2.func_call@401': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes.int',
		},),
	])
	def test___init__(self, expected: dict[str, str]) -> None:
		db = self.fixture.get(SymbolDB)

		if self.__verbose:
			print('\n', '\n'.join([f"'{key}': '{raw.org_path}'," for key, raw in db.raws.items()]))

		for expected_path, expected_org_path in expected.items():
			self.assertEqual('ok' if expected_path in db.raws else expected_path, 'ok')
			self.assertEqual(db.raws[expected_path].org_path, expected_org_path)

		for key, value in db.raws.items():
			self.assertEqual('ok' if key in expected else key, 'ok')

		self.assertEqual(len(db.raws), len(expected))
