from unittest import TestCase

from py2cpp.analize.db import SymbolDB
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestSymbolDB(TestCase):
	fixture = Fixture.make(__file__)
	__verbose = False

	@data_provider([
		({
			# 標準ライブラリー/typingライブラリー(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Any': 'typing.Any',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Generic': 'typing.Generic',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Iterator': 'typing.Iterator',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Sequence': 'typing.Sequence',
			# 標準ライブラリー(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# 標準ライブラリー/templateライブラリー(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.T_Seq': 'py2cpp.compatible.python.template.T_Seq',
			# 標準ライブラリー/embedライブラリー(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.__actual__': 'py2cpp.compatible.python.embed.__actual__',
			# 標準ライブラリー(Declable)
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.append': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.append',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.append.self': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.append.elem': 'py2cpp.compatible.python.template.T_Seq',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.pop': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.pop',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.pop.self': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.list.pop.index': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.id.instance': 'typing.Any',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.print.args': 'typing.Any',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate.iterable': 'typing.Sequence',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.range.size': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_classes.len.iterable': 'typing.Sequence',
			# typingライブラリー/標準ライブラリー(ClassDef)
			'typing.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'typing.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'typing.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'typing.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'typing.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'typing.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'typing.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'typing.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'typing.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'typing.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'typing.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'typing.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'typing.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'typing.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'typing.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'typing.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'typing.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'typing.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'typing.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# typingライブラリー(ClassDef)
			'typing.Any': 'typing.Any',
			'typing.Callable': 'typing.Callable',
			'typing.Generic': 'typing.Generic',
			'typing.Iterator': 'typing.Iterator',
			'typing.Sequence': 'typing.Sequence',
			'typing.TypeVar': 'typing.TypeVar',
			# templateモジュール/標準ライブラリー(ClassDef)
			'py2cpp.compatible.python.template.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'py2cpp.compatible.python.template.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'py2cpp.compatible.python.template.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.template.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'py2cpp.compatible.python.template.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'py2cpp.compatible.python.template.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'py2cpp.compatible.python.template.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'py2cpp.compatible.python.template.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'py2cpp.compatible.python.template.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'py2cpp.compatible.python.template.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'py2cpp.compatible.python.template.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'py2cpp.compatible.python.template.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'py2cpp.compatible.python.template.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'py2cpp.compatible.python.template.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'py2cpp.compatible.python.template.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'py2cpp.compatible.python.template.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'py2cpp.compatible.python.template.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'py2cpp.compatible.python.template.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'py2cpp.compatible.python.template.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# templateモジュール/typingライブラリー(ClassDef)
			'py2cpp.compatible.python.template.TypeVar': 'typing.TypeVar',
			# templateモジュール(ClassDef)
			'py2cpp.compatible.python.template.T_Seq': 'py2cpp.compatible.python.template.T_Seq',
			# embedモジュール/標準ライブラリー(ClassDef)
			'py2cpp.compatible.python.embed.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'py2cpp.compatible.python.embed.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'py2cpp.compatible.python.embed.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.embed.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'py2cpp.compatible.python.embed.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'py2cpp.compatible.python.embed.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'py2cpp.compatible.python.embed.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'py2cpp.compatible.python.embed.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'py2cpp.compatible.python.embed.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'py2cpp.compatible.python.embed.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'py2cpp.compatible.python.embed.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'py2cpp.compatible.python.embed.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'py2cpp.compatible.python.embed.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'py2cpp.compatible.python.embed.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'py2cpp.compatible.python.embed.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'py2cpp.compatible.python.embed.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'py2cpp.compatible.python.embed.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'py2cpp.compatible.python.embed.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'py2cpp.compatible.python.embed.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# embedモジュール/typingライブラリー(ClassDef)
			'py2cpp.compatible.python.embed.Callable': 'typing.Callable',
			'py2cpp.compatible.python.embed.TypeVar': 'typing.TypeVar',
			# embedモジュール(ClassDef)
			'py2cpp.compatible.python.embed.T': 'py2cpp.compatible.python.embed.T',
			'py2cpp.compatible.python.embed.__actual__': 'py2cpp.compatible.python.embed.__actual__',
			'py2cpp.compatible.python.embed.__actual__.decorator': 'py2cpp.compatible.python.embed.__actual__.decorator',
			'py2cpp.compatible.python.embed.__alias__': 'py2cpp.compatible.python.embed.__alias__',
			'py2cpp.compatible.python.embed.__alias__.decorator': 'py2cpp.compatible.python.embed.__alias__.decorator',
			# embedモジュール(Declable)
			'py2cpp.compatible.python.embed.__actual__.name': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.embed.__actual__.decorator.wrapped': 'py2cpp.compatible.python.embed.T',
			'py2cpp.compatible.python.embed.__alias__.name': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'py2cpp.compatible.python.embed.__alias__.decorator.wrapped': 'py2cpp.compatible.python.embed.T',
			# test_db_xyzモジュール/標準ライブラリー(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# test_db_xyzモジュール(ClassDef)
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.X': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz.X',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Y': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Y',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Z': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Z',
			# test_db_xyzモジュール(Declable)
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.X.nx': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Y.ny': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Y.x': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz.X',
			'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Z.nz': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			# エントリーポイント/標準ライブラリー(ClassDef)
			'__main__.int': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'__main__.float': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.float',
			'__main__.str': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'__main__.bool': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.bool',
			'__main__.tuple': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.tuple',
			'__main__.pair_': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.pair_',
			'__main__.list': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'__main__.dict': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.dict',
			'__main__.None': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.None',
			'__main__.Union': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Union',
			'__main__.Unknown': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'__main__.type': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.type',
			'__main__.super': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.super',
			'__main__.Exception': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'__main__.id': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.id',
			'__main__.print': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.print',
			'__main__.enumerate': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.enumerate',
			'__main__.range': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.range',
			'__main__.len': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.len',
			# エントリーポイント/test_db_xyzモジュール(ClassDef)
			'__main__.Z': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz.Z',
			# エントリーポイント(ClassDef)
			'__main__.A': '__main__.A',
			'__main__.A.__init__': '__main__.A.__init__',
			'__main__.B': '__main__.B',
			'__main__.B.B2': '__main__.B.B2',
			'__main__.B.B2.class_func': '__main__.B.B2.class_func',
			'__main__.B.__init__': '__main__.B.__init__',
			'__main__.B.func1': '__main__.B.func1',
			'__main__.B.func2': '__main__.B.func2',
			'__main__.B.func2.closure': '__main__.B.func2.closure',
			# エントリーポイント(Declable)
			'__main__.v': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.int',
			'__main__.A.s': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'__main__.A.__init__.self': '__main__.A',
			'__main__.B.v': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'__main__.B.B2.v': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.str',
			'__main__.B.B2.class_func.cls': '__main__.B.B2',
			'__main__.B.__init__.self': '__main__.B',
			'__main__.B.func1.self': '__main__.B',
			'__main__.B.func1.b': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.list',
			'__main__.B.func1.v': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'__main__.B.func2.self': '__main__.B',
			'__main__.B.func2.for_stmt.i': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
			'__main__.B.func2.e': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Exception',
			'__main__.B.func2.closure.a': 'tests.unit.py2cpp.analize.fixtures.test_db_classes.Unknown',
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
