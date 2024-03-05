import re
from types import UnionType
from unittest import TestCase

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.syntax.ast.dsn import DSN
from rogw.tranp.semantics.errors import UnresolvedSymbolError
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class ASTMapping:
	fixture_module_path = Fixture.fixture_module_path(__file__)

	_start = 6
	_func = 'file_input.function_def'
	_Base = f'file_input.class_def[{_start + 1}]'
	_Sub = f'file_input.class_def[{_start + 2}]'
	_Sub_init = f'{_Sub}.class_def_raw.block.function_def[1]'
	_Sub_first_number = f'{_Sub}.class_def_raw.block.function_def[2]'
	_Sub_local_ref = f'{_Sub}.class_def_raw.block.function_def[3]'
	_Sub_member_ref = f'{_Sub}.class_def_raw.block.function_def[4]'
	_Sub_member_write = f'{_Sub}.class_def_raw.block.function_def[5]'
	_Sub_param_ref = f'{_Sub}.class_def_raw.block.function_def[6]'
	_Sub_list_ref = f'{_Sub}.class_def_raw.block.function_def[7]'
	_Sub_base_ref = f'{_Sub}.class_def_raw.block.function_def[8]'
	_Sub_returns = f'{_Sub}.class_def_raw.block.function_def[9]'
	_Sub_invoke_method = f'{_Sub}.class_def_raw.block.function_def[10]'
	_Sub_decl_with_pop = f'{_Sub}.class_def_raw.block.function_def[11]'
	_Sub_decl_locals = f'{_Sub}.class_def_raw.block.function_def[12]'
	_Sub_assign_with_param = f'{_Sub}.class_def_raw.block.function_def[13]'
	_Sub_relay_access = f'{_Sub}.class_def_raw.block.function_def[14]'
	_Sub_fill_list = f'{_Sub}.class_def_raw.block.function_def[15]'
	_Sub_param_default = f'{_Sub}.class_def_raw.block.function_def[16]'
	_CalcOps = f'file_input.class_def[{_start + 3}]'
	_AliasOps = f'file_input.class_def[{_start + 4}]'
	_TupleOps = f'file_input.class_def[{_start + 5}]'
	_CompOps = f'file_input.class_def[{_start + 6}]'
	_EnumOps = f'file_input.class_def[{_start + 7}]'
	_Nullable = f'file_input.class_def[{_start + 8}]'

	aliases = {
		f'{fixture_module_path}.import.xyz': 'file_input.import_stmt[2]',

		f'{fixture_module_path}.value': 'file_input.anno_assign',

		f'{fixture_module_path}.func.block': f'{_func}.function_def_raw.block',

		'Base': f'{_Base}',
		'Base.__init__.params': f'{_Base}.class_def_raw.block.function_def.function_def_raw.parameters',
		'Base.__init__.return': f'{_Base}.class_def_raw.block.function_def.function_def_raw.typed_none',
		'Base.__init__.block': f'{_Base}.class_def_raw.block.function_def.function_def_raw.block',

		'Sub': f'{_Sub}',
		'Sub.C': f'{_Sub}.class_def_raw.block.class_def',
		'Sub.C.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block',
		'Sub.C.class_func': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def',
		'Sub.C.class_func.params': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'Sub.C.class_func.return': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.typed_getitem',
		'Sub.C.class_func.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'Sub.__init__.params': f'{_Sub_init}.function_def_raw.parameters',
		'Sub.__init__.return': f'{_Sub_init}.function_def_raw.typed_none',
		'Sub.__init__.block': f'{_Sub_init}.function_def_raw.block',
		'Sub.__init__.block': f'{_Sub_init}.function_def_raw.block',
		'Sub.first_number.block': f'{_Sub_first_number}.function_def_raw.block',
		'Sub.local_ref.params': f'{_Sub_local_ref}.function_def_raw.parameters',
		'Sub.local_ref.return': f'{_Sub_local_ref}.function_def_raw.typed_none',
		'Sub.local_ref.block': f'{_Sub_local_ref}.function_def_raw.block',
		'Sub.member_ref.block': f'{_Sub_member_ref}.function_def_raw.block',
		'Sub.member_write.block': f'{_Sub_member_write}.function_def_raw.block',
		'Sub.param_ref.params': f'{_Sub_param_ref}.function_def_raw.parameters',
		'Sub.param_ref.block': f'{_Sub_param_ref}.function_def_raw.block',
		'Sub.list_ref.params': f'{_Sub_list_ref}.function_def_raw.parameters',
		'Sub.list_ref.block': f'{_Sub_list_ref}.function_def_raw.block',
		'Sub.base_ref.block': f'{_Sub_base_ref}.function_def_raw.block',
		'Sub.returns.return': f'{_Sub_returns}.function_def_raw.typed_var',
		'Sub.returns.block': f'{_Sub_returns}.function_def_raw.block',
		'Sub.invoke_method.block': f'{_Sub_invoke_method}.function_def_raw.block',
		'Sub.decl_with_pop.block': f'{_Sub_decl_with_pop}.function_def_raw.block',
		'Sub.decl_locals.block': f'{_Sub_decl_locals}.function_def_raw.block',
		'Sub.decl_locals.closure.block': f'{_Sub_decl_locals}.function_def_raw.block.function_def.function_def_raw.block',

		'CompOps.list_comp.block': f'{_CompOps}.class_def_raw.block.function_def[0].function_def_raw.block',

		'Nullable.returns.return': f'{_Nullable}.class_def_raw.block.function_def[1].function_def_raw.typed_or_expr',
		'Nullable.var_move.block': f'{_Nullable}.class_def_raw.block.function_def[2].function_def_raw.block',
	}


def _ast(before: str, after: str) -> str:
	return DSN.join(ASTMapping.aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.rogw.tranp.semantics.fixtures.test_provider_xyz',
		'classes': 'rogw.tranp.compatible.libralies.classes',
	}
	return DSN.join(aliases[before], after)


class TestReflections(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		(f'{fixture_module_path}.Sub.decl_locals.a', list, False),
		(f'{fixture_module_path}.Sub.decl_locals.closure.b', list, True),
		(f'{fixture_module_path}.Sub.decl_locals.a', dict, False),
		(f'{fixture_module_path}.Sub.decl_locals.closure.b', dict, False),
		(f'{fixture_module_path}.AliasOps.func.d', list, False),
		(f'{fixture_module_path}.AliasOps.func.d', dict, False),  # XXX エイリアスはdictそのものではないが要検討
	])
	def test_is_a(self, fullyname: str, standard_type: type[Standards], expected: bool) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(fullyname)
		self.assertEqual(reflections.is_a(symbol, standard_type), expected)

	@data_provider([
		(f'{fixture_module_path}.TypeAlias', 'TypeAlias'),

		(f'{fixture_module_path}.Z', 'Z'),

		(f'{fixture_module_path}.value', 'int'),

		(f'{fixture_module_path}.Base', 'Base'),
		(f'{fixture_module_path}.Base.base_str', 'str'),

		(f'{fixture_module_path}.Sub', 'Sub'),

		(f'{fixture_module_path}.Sub.C', 'C'),
		(f'{fixture_module_path}.Sub.C.value', 'str'),
		(f'{fixture_module_path}.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),

		(f'{fixture_module_path}.Sub.numbers', 'list<int>'),

		(f'{fixture_module_path}.Sub.__init__', '__init__(Sub) -> None'),
		(f'{fixture_module_path}.Sub.__init__.self', 'Sub'),

		(f'{fixture_module_path}.Sub.local_ref', 'local_ref(Sub) -> None'),
		(f'{fixture_module_path}.Sub.local_ref.self', 'Sub'),
		(f'{fixture_module_path}.Sub.local_ref.value', 'bool'),

		(f'{fixture_module_path}.Sub.member_ref', 'member_ref(Sub) -> None'),
		(f'{fixture_module_path}.Sub.member_ref.self', 'Sub'),
		(f'{fixture_module_path}.Sub.member_write', 'member_write(Sub) -> None'),
		(f'{fixture_module_path}.Sub.member_write.self', 'Sub'),

		(f'{fixture_module_path}.Sub.param_ref', 'param_ref(Sub, int) -> None'),
		(f'{fixture_module_path}.Sub.param_ref.self', 'Sub'),
		(f'{fixture_module_path}.Sub.param_ref.param', 'int'),

		(f'{fixture_module_path}.Sub.list_ref', 'list_ref(Sub, list<Sub>) -> None'),
		(f'{fixture_module_path}.Sub.list_ref.self', 'Sub'),
		(f'{fixture_module_path}.Sub.list_ref.subs', 'list<Sub>'),

		(f'{fixture_module_path}.Sub.base_ref', 'base_ref(Sub) -> None'),
		(f'{fixture_module_path}.Sub.base_ref.self', 'Sub'),

		(f'{fixture_module_path}.Sub.returns', 'returns(Sub) -> str'),
		(f'{fixture_module_path}.Sub.returns.self', 'Sub'),

		(f'{fixture_module_path}.Sub.invoke_method', 'invoke_method(Sub) -> None'),
		(f'{fixture_module_path}.Sub.invoke_method.self', 'Sub'),

		(f'{fixture_module_path}.Sub.decl_with_pop.poped', 'int'),

		(f'{fixture_module_path}.Sub.decl_locals', 'decl_locals(Sub) -> int'),
		(f'{fixture_module_path}.Sub.decl_locals.a', 'int'),
		(f'{fixture_module_path}.Sub.decl_locals.closure', 'closure() -> list<int>'),
		(f'{fixture_module_path}.Sub.decl_locals.closure.b', 'list<int>'),
		(f'{fixture_module_path}.Sub.decl_locals.if.for.i', 'int'),
		(f'{fixture_module_path}.Sub.decl_locals.if.for.try.e', 'Exception'),

		(f'{fixture_module_path}.Sub.relay_access.s', 'str'),

		(f'{fixture_module_path}.Sub.fill_list.n_x3', 'list<int>'),

		(f'{fixture_module_path}.Sub.param_default.d', 'DSI=dict<str, int>'),
		(f'{fixture_module_path}.Sub.param_default.n', 'int'),
		(f'{fixture_module_path}.Sub.param_default.n2', 'int'),
		(f'{fixture_module_path}.Sub.param_default.keys', 'list<str>'),

		(f'{fixture_module_path}.CalcOps.unary.n_neg', 'int'),
		(f'{fixture_module_path}.CalcOps.unary.n_not', 'bool'),
		(f'{fixture_module_path}.CalcOps.binary.n', 'int'),
		(f'{fixture_module_path}.CalcOps.binary.nb0', 'int'),
		(f'{fixture_module_path}.CalcOps.binary.nb1', 'int'),
		(f'{fixture_module_path}.CalcOps.binary.fn0', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.fn1', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.fn2', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.fb0', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.fb1', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.result', 'float'),
		(f'{fixture_module_path}.CalcOps.binary.l_in', 'bool'),
		(f'{fixture_module_path}.CalcOps.binary.l_not_in', 'bool'),
		(f'{fixture_module_path}.CalcOps.binary.n_is', 'bool'),
		(f'{fixture_module_path}.CalcOps.binary.n_is_not', 'bool'),
		(f'{fixture_module_path}.CalcOps.tenary.n', 'int'),
		(f'{fixture_module_path}.CalcOps.tenary.s', 'str'),
		(f'{fixture_module_path}.CalcOps.tenary.s_or_null', 'Union<str, None>'),

		(f'{fixture_module_path}.AliasOps.func', 'func(AliasOps, Z2=Z) -> None'),
		(f'{fixture_module_path}.AliasOps.func.z2', 'Z2=Z'),
		(f'{fixture_module_path}.AliasOps.func.d', 'DSI=dict<str, int>'),
		(f'{fixture_module_path}.AliasOps.func.d_in_v', 'int'),
		(f'{fixture_module_path}.AliasOps.func.d2', 'DSI2=dict<str, DSI=dict<str, int>>'),
		(f'{fixture_module_path}.AliasOps.func.d2_in_dsi', 'DSI=dict<str, int>'),
		(f'{fixture_module_path}.AliasOps.func.d2_in_dsi_in_v', 'int'),
		(f'{fixture_module_path}.AliasOps.func.z2_in_x', 'X'),
		(f'{fixture_module_path}.AliasOps.func.new_z2_in_x', 'X'),

		(f'{fixture_module_path}.TupleOps.unpack.for.key0', 'str'),
		(f'{fixture_module_path}.TupleOps.unpack.for.value0', 'int'),
		(f'{fixture_module_path}.TupleOps.unpack.for.value1', 'int'),
		(f'{fixture_module_path}.TupleOps.unpack.for.key1', 'str'),
		(f'{fixture_module_path}.TupleOps.unpack.for.pair0', 'Pair<str, int>'),
		(f'{fixture_module_path}.TupleOps.unpack.for.key10', 'str'),
		(f'{fixture_module_path}.TupleOps.unpack.for.value10', 'DSI=dict<str, int>'),
		(f'{fixture_module_path}.TupleOps.unpack.for.value11', 'DSI=dict<str, int>'),
		(f'{fixture_module_path}.TupleOps.unpack.for.key11', 'str'),
		(f'{fixture_module_path}.TupleOps.unpack.for.pair10', 'Pair<str, DSI=dict<str, int>>'),

		(f'{fixture_module_path}.TupleOps.unpack_assign.a', 'str'),  # XXX Pythonのシンタックス上は不正。一旦保留
		(f'{fixture_module_path}.TupleOps.unpack_assign.b', 'int'),  # XXX 〃

		(f'{fixture_module_path}.CompOps.list_comp.values0', 'list<int>'),
		(f'{fixture_module_path}.CompOps.list_comp.values1', 'list<int>'),
		(f'{fixture_module_path}.CompOps.list_comp.values2', 'list<int>'),
		(f'{fixture_module_path}.CompOps.list_comp.strs', 'list<str>'),
		(f'{fixture_module_path}.CompOps.list_comp.value', 'int'),

		(f'{fixture_module_path}.CompOps.dict_comp.kvs0', 'dict<str, int>'),
		(f'{fixture_module_path}.CompOps.dict_comp.kvs1', 'dict<str, int>'),
		(f'{fixture_module_path}.CompOps.dict_comp.kvs2', 'dict<str, int>'),

		(f'{fixture_module_path}.EnumOps.Values', 'Values'),
		(f'{fixture_module_path}.EnumOps.Values.A', 'int'),  # Enumの定数値を直接参照するとEnum型ではなく、オリジナルの型になる ※情報を損なわないようにするため
		(f'{fixture_module_path}.EnumOps.Values.B', 'int'),  # 〃
		(f'{fixture_module_path}.EnumOps.cls_assign.a', 'Values'),
		(f'{fixture_module_path}.EnumOps.cls_assign.d', 'dict<Values, str>'),
		(f'{fixture_module_path}.EnumOps.cls_assign.da', 'str'),
		(f'{fixture_module_path}.EnumOps.assign.a', 'Values'),
		(f'{fixture_module_path}.EnumOps.assign.d', 'dict<Values, str>'),
		(f'{fixture_module_path}.EnumOps.assign.da', 'str'),
		(f'{fixture_module_path}.EnumOps.cast.e', 'Values'),
		(f'{fixture_module_path}.EnumOps.cast.n', 'int'),

		(f'{fixture_module_path}.Nullable.params.base', 'Union<Base, None>'),
		(f'{fixture_module_path}.Nullable.accessible.sub', 'Union<Sub, None>'),
		(f'{fixture_module_path}.Nullable.accessible.subs', 'Union<list<Sub>, None>'),
		(f'{fixture_module_path}.Nullable.accessible.s', 'str'),
		(f'{fixture_module_path}.Nullable.accessible.n', 'int'),
	])
	def test_from_fullyname(self, fullyname: str, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(fullyname)
		self.assertEqual(str(symbol), expected)

	@data_provider([
		(f'{fixture_module_path}.CalcOps.tenary.n_or_s', UnresolvedSymbolError, r'Only Nullable.'),
		(f'{fixture_module_path}.Nullable.accessible.arr', UnresolvedSymbolError, r'Only Nullable.'),
	])
	def test_from_fullyname_error(self, fullyname: str, expected_error: type[Exception], expected: re.Pattern[str]) -> None:
		reflections = self.fixture.get(Reflections)
		with self.assertRaisesRegex(expected_error, expected):
			str(reflections.from_fullyname(fullyname))

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
		(UnionType, _mod('classes', 'Union')),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_standard(self, standard_type: type[Standards] | None, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		self.assertEqual(reflections.type_of_standard(standard_type).types.fullyname, expected)

	@data_provider([
		(_ast(f'{fixture_module_path}.import.xyz', 'import_names.name'), _mod('xyz', 'Z'), 'Z'),
		(_ast(f'{fixture_module_path}.value', 'assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast(f'{fixture_module_path}.value', 'typed_var'), _mod('classes', 'int'), 'int'),
		(_ast(f'{fixture_module_path}.value', 'number'), _mod('classes', 'int'), 'int'),

		(_ast('Base', ''), f'{fixture_module_path}.Base', 'Base'),
		(_ast('Base', 'class_def_raw.name'), f'{fixture_module_path}.Base', 'Base'),

		(_ast('Base.__init__.params', 'paramvalue.typedparam.name'), f'{fixture_module_path}.Base', 'Base'),
		(_ast('Base.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Base.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'comment_stmt'), _mod('classes', 'Unknown'), 'Unknown'),

		(_ast('Sub', ''), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.name'), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), f'{fixture_module_path}.Base', 'Base'),

		(_ast('Sub.C', ''), f'{fixture_module_path}.Sub.C', 'C'),
		(_ast('Sub.C.block', 'anno_assign.assign_namelist.var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.C.block', 'anno_assign.string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.C.class_func', ''), f'{fixture_module_path}.Sub.C.class_func', 'class_func(C) -> dict<str, int>'),
		(_ast('Sub.C.class_func.params', 'paramvalue.typedparam.name'), f'{fixture_module_path}.Sub.C', 'C'),
		(_ast('Sub.C.class_func.return', ''), _mod('classes', 'dict'), 'dict<str, int>'),
		(_ast('Sub.C.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),

		(_ast('Sub.__init__.params', 'paramvalue.typedparam.name'), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Sub.__init__.block', 'funccall'), f'{fixture_module_path}.Base', 'Base'),
		(_ast('Sub.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('Sub.__init__.block', 'anno_assign'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.typed_getitem'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign.list'), _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		(_ast('Sub.first_number.block', 'return_stmt'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.local_ref.params', 'paramvalue.typedparam.name'), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub.local_ref.block', 'assign'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.block', 'funccall.var'), _mod('classes', 'print'), 'print(Any) -> None'),
		(_ast('Sub.local_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.return', ''), _mod('classes', 'None'), 'None'),

		(_ast('Sub.member_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.member_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.member_write.block', 'assign[0].assign_namelist.getattr'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[0].number'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[1].assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.member_write.block', 'assign[1].string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.param_ref.params', 'paramvalue[0].typedparam.name'), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub.param_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.param_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.list_ref.params', 'paramvalue[0].typedparam.name'), f'{fixture_module_path}.Sub', 'Sub'),
		(_ast('Sub.list_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<Sub>'),
		(_ast('Sub.list_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.list_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.base_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.returns.return', ''), _mod('classes', 'str'), 'str'),
		(_ast('Sub.returns.block', 'return_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.invoke_method.block', 'funccall.getattr'), f'{fixture_module_path}.Sub.invoke_method', 'invoke_method(Sub) -> None'),

		(_ast('Sub.decl_with_pop.block', 'assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_with_pop.block', 'assign.funccall'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.decl_locals.block', 'if_stmt.block.assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_locals.closure.block', 'assign.assign_namelist.var'), _mod('classes', 'list'), 'list<int>'),

		(_ast('CompOps.list_comp.block', 'aug_assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('CompOps.list_comp.block', 'aug_assign.getitem'), _mod('classes', 'float'), 'float'),

		(_ast('Nullable.returns.return', ''), _mod('classes', 'Union'), 'Union<Base, None>'),
		(_ast('Nullable.var_move.block', 'if_stmt.block.return_stmt'), _mod('classes', 'str'), 'str'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		node = self.fixture.shared_nodes_by(full_path)
		symbol = reflections.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)