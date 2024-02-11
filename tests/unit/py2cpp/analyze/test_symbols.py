from unittest import TestCase

from py2cpp.analyze.symbols import Symbols
from py2cpp.ast.dsn import DSN
import py2cpp.compatible.python.classes as classes
from py2cpp.compatible.python.types import Primitives
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'__main__': 'file_input',
		'__main__.func.block': 'file_input.function_def.function_def_raw.block',
		'Base': 'file_input.class_def[3]',
		'Base.__init__.params': 'file_input.class_def[3].class_def_raw.block.function_def.function_def_raw.parameters',
		'Base.__init__.return': 'file_input.class_def[3].class_def_raw.block.function_def.function_def_raw.return_type',
		'Base.__init__.block': 'file_input.class_def[3].class_def_raw.block.function_def.function_def_raw.block',
		'Sub': 'file_input.class_def[4]',
		'Sub.B2': 'file_input.class_def[4].class_def_raw.block.class_def',
		'Sub.B2.block': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block',
		'Sub.B2.class_func': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def',
		'Sub.B2.class_func.params': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'Sub.B2.class_func.return': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.return_type',
		'Sub.B2.class_func.block': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'Sub.__init__.params': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.parameters',
		'Sub.__init__.return': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.return_type',
		'Sub.__init__.block': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.block',
		'Sub.func1.params': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.parameters',
		'Sub.func1.return': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.return_type',
		'Sub.func1.block': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block',
		'Sub.func2.block': 'file_input.class_def[4].class_def_raw.block.function_def[3].function_def_raw.block',
		'Sub.func2.closure.block': 'file_input.class_def[4].class_def_raw.block.function_def[3].function_def_raw.block.function_def.function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.py2cpp.analyze.fixtures.test_db_xyz',
		'classes': 'tests.unit.py2cpp.analyze.fixtures.test_db_classes',
	}
	return DSN.join(aliases[before], after)


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('__main__.Sub.func2.a', list, False),
		('__main__.Sub.func2.closure.b', list, True),
		('__main__.func.d', list, False),
		('__main__.Sub.func2.a', dict, False),
		('__main__.Sub.func2.closure.b', dict, False),
		('__main__.func.d', dict, False),  # XXX エイリアスなのでdictでそのものではないが、要検討
	])
	def test_is_a(self, fullyname: str, primitive_type: type[Primitives], expected: bool) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(symbols.is_a(symbol, primitive_type), expected)

	@data_provider([
		('__main__.v', 'int'),
		('__main__.Base', 'Base'),
		('__main__.Base.s', 'str'),
		('__main__.Sub', 'Sub'),
		('__main__.Sub.v', 'list<int>'),
		# 5
		('__main__.Sub.__init__', '__init__(Sub) -> None'),
		('__main__.Sub.__init__.self', 'Sub'),
		('__main__.Sub.func1', 'func1(Sub, list<Sub>) -> str'),
		('__main__.Sub.func1.self', 'Sub'),
		('__main__.Sub.func1.b', 'list<Sub>'),
		# 10
		('__main__.Sub.func1.v', 'bool'),
		('__main__.Sub.func1.v2', 'int'),
		('__main__.Sub.func2', 'func2(Sub) -> int'),
		('__main__.Sub.func2.a', 'int'),
		('__main__.Sub.func2.closure', 'closure() -> list<int>'),
		# 15
		('__main__.Sub.func2.closure.b', 'list<int>'),
		('__main__.Sub.func2.if.for.i', 'int'),
		('__main__.Sub.func2.if.for.try.e', 'Exception'),
		('__main__.Sub.B2', 'B2'),
		('__main__.Sub.B2.class_func', 'class_func(B2) -> dict<str, int>'),
		# 20
		('__main__.func', 'func(Z2=Z) -> None'),
		('__main__.func.z2', 'Z2=Z'),
		('__main__.func.d', 'DSI=dict<str, int>'),
		('__main__.func.d_in_v', 'int'),
		('__main__.func.d2', 'DSI2=dict<str, DSI=dict<str, int>>'),
		# 25
		('__main__.func.d2_in_dsi', 'DSI=dict<str, int>'),
		('__main__.func.d2_in_dsi_in_v', 'int'),
		('__main__.func.z2_in_x', 'X'),
		('__main__.func.new_z2_in_x', 'X'),
	])
	def test_from_fullyname(self, fullyname: str, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(str(symbol), expected)

	@data_provider([
		(int, _mod('classes', int.__name__)),
		(float, _mod('classes', float.__name__)),
		(str, _mod('classes', str.__name__)),
		(bool, _mod('classes', bool.__name__)),
		(tuple, _mod('classes', tuple.__name__)),
		(classes.Pair, _mod('classes', classes.Pair.__name__)),
		(list, _mod('classes', list.__name__)),
		(dict, _mod('classes', dict.__name__)),
		(classes.Unknown, _mod('classes', classes.Unknown.__name__)),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_primitive(self, primitive_type: type[Primitives] | None, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		self.assertEqual(symbols.type_of_primitive(primitive_type).types.fullyname, expected)

	@data_provider([
		(_ast('__main__', 'import_stmt[1].import_names.name'), _mod('xyz', 'Z'), 'Z'),
		(_ast('__main__', 'anno_assign.var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.typed_var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.number'), _mod('classes', 'int'), 'int'),
		(_ast('Base', ''), '__main__.Base', 'Base'),
		# 5
		(_ast('Base', 'class_def_raw.name'), '__main__.Base', 'Base'),
		(_ast('Base.__init__.params', 'paramvalue.typedparam.name'), '__main__.Base', 'Base'),
		(_ast('Base.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		(_ast('Base.__init__.block', 'anno_assign.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		# 10
		(_ast('Base.__init__.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('Sub', ''), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), '__main__.Base', 'Base'),
		(_ast('Sub.B2', ''), '__main__.Sub.B2', 'B2'),
		# 15
		(_ast('Sub.B2.block', 'anno_assign.var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.B2.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.B2.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.B2.class_func', ''), '__main__.Sub.B2.class_func', 'class_func(B2) -> dict<str, int>'),
		(_ast('Sub.B2.class_func.params', 'paramvalue.typedparam.name'), '__main__.Sub.B2', 'B2'),
		# 20
		(_ast('Sub.B2.class_func.return', 'typed_getitem'), _mod('classes', 'dict'), 'dict'), # XXX 関数の戻り値の型は関数のシンボル経由でのみ取得できる
		(_ast('Sub.B2.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),
		(_ast('Sub.__init__.params', 'paramvalue.typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		(_ast('Sub.__init__.block', 'funccall'), '__main__.Base', 'Base'),
		# 25
		(_ast('Sub.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('Sub.__init__.block', 'anno_assign'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.typed_getitem'), _mod('classes', 'list'), 'list'), # XXX 型はシンボル経由でのみ取得できる
		(_ast('Sub.__init__.block', 'anno_assign.list'), _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる
		# 30
		(_ast('Sub.func1.params', 'paramvalue[0].typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.func1.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<Sub>'),
		(_ast('Sub.func1.return', 'typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.func1.block', 'assign[0].var'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.func1.block', 'assign[0].const_false'), _mod('classes', 'bool'), 'bool'),
		# 35
		(_ast('Sub.func1.block', 'funccall[1].arguments.argvalue.var'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.func1.block', 'funccall[2].arguments.argvalue.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.func1.block', 'funccall[3].arguments.argvalue.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.func1.block', 'assign[4].getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.func1.block', 'assign[4].string'), _mod('classes', 'str'), 'str'),
		# 40
		(_ast('Sub.func1.block', 'assign[5].getattr'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.func1.block', 'assign[5].number'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.func1.block', 'assign[6]'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.func1.block', 'funccall[7].arguments.argvalue.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.func1.block', 'return_stmt.getattr'), _mod('classes', 'str'), 'str'),
		# 45
		(_ast('Sub.func2.block', 'if_stmt.block.assign.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.func2.closure.block', 'assign.var'), _mod('classes', 'list'), 'list<int>'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		symbol = symbols.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)
