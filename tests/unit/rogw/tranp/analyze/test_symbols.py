from unittest import TestCase

from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.ast.dsn import DSN
import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.compatible.python.types import Primitives
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
		'Sub.C': 'file_input.class_def[4].class_def_raw.block.class_def',
		'Sub.C.block': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block',
		'Sub.C.class_func': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def',
		'Sub.C.class_func.params': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'Sub.C.class_func.return': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.return_type',
		'Sub.C.class_func.block': 'file_input.class_def[4].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'Sub.__init__.params': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.parameters',
		'Sub.__init__.return': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.return_type',
		'Sub.__init__.block': 'file_input.class_def[4].class_def_raw.block.function_def[1].function_def_raw.block',
		'Sub.local_ref.params': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.parameters',
		'Sub.local_ref.return': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.return_type',
		'Sub.local_ref.block': 'file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block',
		'Sub.member_ref.block': 'file_input.class_def[4].class_def_raw.block.function_def[3].function_def_raw.block',
		'Sub.member_write.block': 'file_input.class_def[4].class_def_raw.block.function_def[4].function_def_raw.block',
		'Sub.param_ref.params': 'file_input.class_def[4].class_def_raw.block.function_def[5].function_def_raw.parameters',
		'Sub.param_ref.block': 'file_input.class_def[4].class_def_raw.block.function_def[5].function_def_raw.block',
		'Sub.list_ref.params': 'file_input.class_def[4].class_def_raw.block.function_def[6].function_def_raw.parameters',
		'Sub.list_ref.block': 'file_input.class_def[4].class_def_raw.block.function_def[6].function_def_raw.block',
		'Sub.base_ref.block': 'file_input.class_def[4].class_def_raw.block.function_def[7].function_def_raw.block',
		'Sub.returns.return': 'file_input.class_def[4].class_def_raw.block.function_def[8].function_def_raw.return_type',
		'Sub.returns.block': 'file_input.class_def[4].class_def_raw.block.function_def[8].function_def_raw.block',
		'Sub.invoke_method.block': 'file_input.class_def[4].class_def_raw.block.function_def[9].function_def_raw.block',
		'Sub.decl_with_pop.block': 'file_input.class_def[4].class_def_raw.block.function_def[10].function_def_raw.block',
		'Sub.decl_locals.block': 'file_input.class_def[4].class_def_raw.block.function_def[11].function_def_raw.block',
		'Sub.decl_locals.closure.block': 'file_input.class_def[4].class_def_raw.block.function_def[11].function_def_raw.block.function_def.function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz',
		'classes': 'rogw.tranp.compatible.python.classes',
	}
	return DSN.join(aliases[before], after)


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('__main__.Sub.decl_locals.a', list, False),
		('__main__.Sub.decl_locals.closure.b', list, True),
		('__main__.Sub.decl_locals.a', dict, False),
		('__main__.Sub.decl_locals.closure.b', dict, False),
		('__main__.AliasCheck.func.d', list, False),
		('__main__.AliasCheck.func.d', dict, False),  # XXX エイリアスなのでdictでそのものではないが、要検討
	])
	def test_is_a(self, fullyname: str, primitive_type: type[Primitives], expected: bool) -> None:
		symbols = self.fixture.get(Symbols)
		symbol = symbols.from_fullyname(fullyname)
		self.assertEqual(symbols.is_a(symbol, primitive_type), expected)

	@data_provider([
		('__main__.value', 'int'),

		('__main__.Base', 'Base'),
		('__main__.Base.base_str', 'str'),

		('__main__.Sub', 'Sub'),

		('__main__.Sub.C', 'C'),
		('__main__.Sub.C.value', 'str'),
		('__main__.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),

		('__main__.Sub.numbers', 'list<int>'),

		('__main__.Sub.__init__', '__init__(Sub) -> None'),
		('__main__.Sub.__init__.self', 'Sub'),

		('__main__.Sub.local_ref', 'local_ref(Sub) -> None'),
		('__main__.Sub.local_ref.self', 'Sub'),
		('__main__.Sub.local_ref.value', 'bool'),

		('__main__.Sub.member_ref', 'member_ref(Sub) -> None'),
		('__main__.Sub.member_ref.self', 'Sub'),
		('__main__.Sub.member_write', 'member_write(Sub) -> None'),
		('__main__.Sub.member_write.self', 'Sub'),

		('__main__.Sub.param_ref', 'param_ref(Sub, int) -> None'),
		('__main__.Sub.param_ref.self', 'Sub'),
		('__main__.Sub.param_ref.param', 'int'),

		('__main__.Sub.list_ref', 'list_ref(Sub, list<Sub>) -> None'),
		('__main__.Sub.list_ref.self', 'Sub'),
		('__main__.Sub.list_ref.subs', 'list<Sub>'),

		('__main__.Sub.base_ref', 'base_ref(Sub) -> None'),
		('__main__.Sub.base_ref.self', 'Sub'),

		('__main__.Sub.returns', 'returns(Sub) -> str'),
		('__main__.Sub.returns.self', 'Sub'),

		('__main__.Sub.invoke_method', 'invoke_method(Sub) -> None'),
		('__main__.Sub.invoke_method.self', 'Sub'),

		('__main__.Sub.decl_with_pop.poped', 'int'),

		('__main__.Sub.decl_locals', 'decl_locals(Sub) -> int'),
		('__main__.Sub.decl_locals.a', 'int'),
		('__main__.Sub.decl_locals.closure', 'closure() -> list<int>'),
		('__main__.Sub.decl_locals.closure.b', 'list<int>'),
		('__main__.Sub.decl_locals.if.for.i', 'int'),
		('__main__.Sub.decl_locals.if.for.try.e', 'Exception'),

		('__main__.Ops.sum.n', 'int'),
		('__main__.Ops.sum.nb0', 'int'),
		('__main__.Ops.sum.nb1', 'int'),
		('__main__.Ops.sum.fn0', 'float'),
		('__main__.Ops.sum.fn1', 'float'),
		('__main__.Ops.sum.fn2', 'float'),
		('__main__.Ops.sum.fb0', 'float'),
		('__main__.Ops.sum.fb1', 'float'),

		('__main__.AliasCheck.func', 'func(AliasCheck, Z2=Z) -> None'),
		('__main__.AliasCheck.func.z2', 'Z2=Z'),
		('__main__.AliasCheck.func.d', 'DSI=dict<str, int>'),
		('__main__.AliasCheck.func.d_in_v', 'int'),
		('__main__.AliasCheck.func.d2', 'DSI2=dict<str, DSI=dict<str, int>>'),
		('__main__.AliasCheck.func.d2_in_dsi', 'DSI=dict<str, int>'),
		('__main__.AliasCheck.func.d2_in_dsi_in_v', 'int'),
		('__main__.AliasCheck.func.z2_in_x', 'X'),
		('__main__.AliasCheck.func.new_z2_in_x', 'X'),

		('__main__.TupleCheck.unpack.for.key0', 'str'),
		('__main__.TupleCheck.unpack.for.value0', 'int'),
		('__main__.TupleCheck.unpack.for.value1', 'int'),
		('__main__.TupleCheck.unpack.for.key1', 'str'),
		('__main__.TupleCheck.unpack.for.pair0', 'Pair<str, int>'),
		('__main__.TupleCheck.unpack.for.key10', 'str'),
		('__main__.TupleCheck.unpack.for.value10', 'DSI=dict<str, int>'),
		('__main__.TupleCheck.unpack.for.value11', 'DSI=dict<str, int>'),
		('__main__.TupleCheck.unpack.for.key11', 'str'),
		('__main__.TupleCheck.unpack.for.pair10', 'Pair<str, DSI=dict<str, int>>'),

		('__main__.TupleCheck.unpack_assign.a', 'str'),  # XXX Pythonのシンタックス上は不正。一旦保留
		('__main__.TupleCheck.unpack_assign.b', 'int'),  # XXX 〃
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
		(_ast('__main__', 'anno_assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.typed_var'), _mod('classes', 'int'), 'int'),
		(_ast('__main__', 'anno_assign.number'), _mod('classes', 'int'), 'int'),

		(_ast('Base', ''), '__main__.Base', 'Base'),
		(_ast('Base', 'class_def_raw.name'), '__main__.Base', 'Base'),

		(_ast('Base.__init__.params', 'paramvalue.typedparam.name'), '__main__.Base', 'Base'),
		(_ast('Base.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		(_ast('Base.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub', ''), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), '__main__.Base', 'Base'),

		(_ast('Sub.C', ''), '__main__.Sub.C', 'C'),
		(_ast('Sub.C.block', 'anno_assign.assign_namelist.var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.C.class_func', ''), '__main__.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),
		(_ast('Sub.C.class_func.params', 'paramvalue.typedparam.name'), '__main__.Sub.C', 'C'),
		(_ast('Sub.C.class_func.return', ''), _mod('classes', 'dict'), 'dict'),  # XXX 関数の戻り値の型は関数のシンボル経由でのみ取得できる
		(_ast('Sub.C.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),

		(_ast('Sub.__init__.params', 'paramvalue.typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.__init__.return', 'typed_none'), _mod('classes', 'None'), 'None'),
		(_ast('Sub.__init__.block', 'funccall'), '__main__.Base', 'Base'),
		(_ast('Sub.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('Sub.__init__.block', 'anno_assign'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.typed_getitem'), _mod('classes', 'list'), 'list'),  # XXX 型はシンボル経由でのみ取得できる
		(_ast('Sub.__init__.block', 'anno_assign.list'), _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		(_ast('Sub.local_ref.params', 'paramvalue.typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.local_ref.block', 'assign'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.block', 'funccall.var'), _mod('classes', 'print'), 'print(Any) -> None'),
		(_ast('Sub.local_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.return', ''), _mod('classes', 'None'), 'None'),

		(_ast('Sub.member_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.member_write.block', 'assign[0].assign_namelist.getattr'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[0].number'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[1].assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.member_write.block', 'assign[1].string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.param_ref.params', 'paramvalue[0].typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.param_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.param_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.list_ref.params', 'paramvalue[0].typedparam.name'), '__main__.Sub', 'Sub'),
		(_ast('Sub.list_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<Sub>'),
		(_ast('Sub.list_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.list_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.base_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.returns.return', ''), _mod('classes', 'str'), 'str'),
		(_ast('Sub.returns.block', 'return_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.invoke_method.block', 'funccall.getattr'), '__main__.Sub.invoke_method', 'invoke_method(Sub) -> None'),

		(_ast('Sub.decl_with_pop.block', 'assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_with_pop.block', 'assign.funccall'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.decl_locals.block', 'if_stmt.block.assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_locals.closure.block', 'assign.assign_namelist.var'), _mod('classes', 'list'), 'list<int>'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		symbol = symbols.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)
