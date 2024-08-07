from unittest import TestCase

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class ASTMapping:
	fixture_module_path = Fixture.fixture_module_path(__file__)

	_import_xyz = 4
	_start = 8
	_func = 'file_input.function_def'
	_Base = f'file_input.class_def[{_start + 1}]'
	_Sub = f'file_input.class_def[{_start + 2}]'
	_Sub_init = f'{_Sub}.class_def_raw.block.function_def[2]'
	_Sub_first_number = f'{_Sub}.class_def_raw.block.function_def[4]'
	_Sub_local_ref = f'{_Sub}.class_def_raw.block.function_def[5]'
	_Sub_member_ref = f'{_Sub}.class_def_raw.block.function_def[6]'
	_Sub_member_write = f'{_Sub}.class_def_raw.block.function_def[7]'
	_Sub_param_ref = f'{_Sub}.class_def_raw.block.function_def[8]'
	_Sub_list_ref = f'{_Sub}.class_def_raw.block.function_def[9]'
	_Sub_base_ref = f'{_Sub}.class_def_raw.block.function_def[10]'
	_Sub_returns = f'{_Sub}.class_def_raw.block.function_def[11]'
	_Sub_yields = f'{_Sub}.class_def_raw.block.function_def[12]'
	_Sub_invoke_method = f'{_Sub}.class_def_raw.block.function_def[13]'
	_Sub_decl_with_pop = f'{_Sub}.class_def_raw.block.function_def[14]'
	_Sub_decl_locals = f'{_Sub}.class_def_raw.block.function_def[15]'
	_Sub_assign_with_param = f'{_Sub}.class_def_raw.block.function_def[16]'
	_Sub_relay_access = f'{_Sub}.class_def_raw.block.function_def[17]'
	_Sub_fill_list = f'{_Sub}.class_def_raw.block.function_def[18]'
	_Sub_param_default = f'{_Sub}.class_def_raw.block.function_def[19]'
	_Sub_Base = f'{_Sub}.class_def_raw.block.function_def[20]'
	_Sub_kw_params = f'{_Sub}.class_def_raw.block.function_def[21]'
	_CalcOps = f'file_input.class_def[{_start + 3}]'
	_AliasOps = f'file_input.class_def[{_start + 4}]'
	_TupleOps = f'file_input.class_def[{_start + 5}]'
	_CompOps = f'file_input.class_def[{_start + 6}]'
	_EnumOps = f'file_input.class_def[{_start + 7}]'
	_Nullable = f'file_input.class_def[{_start + 8}]'
	_TypeT = '',
	_GenericOps = f'file_input.class_def[{_start + 10}]'
	_WithOps = f'file_input.class_def[{_start + 11}]'

	aliases = {
		ModuleDSN.full_joined(fixture_module_path, 'import.xyz'): f'file_input.import_stmt[{_import_xyz}]',

		ModuleDSN.full_joined(fixture_module_path, 'value'): 'file_input.anno_assign',

		ModuleDSN.full_joined(fixture_module_path, 'func.block'): f'{_func}.function_def_raw.block',

		'Base': f'{_Base}',
		'Base.__init__.params': f'{_Base}.class_def_raw.block.function_def.function_def_raw.parameters',
		'Base.__init__.return': f'{_Base}.class_def_raw.block.function_def.function_def_raw.typed_none',
		'Base.__init__.block': f'{_Base}.class_def_raw.block.function_def.function_def_raw.block',

		'Sub': f'{_Sub}',
		'Sub.Inner': f'{_Sub}.class_def_raw.block.class_def',
		'Sub.Inner.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block',
		'Sub.Inner.class_func': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def',
		'Sub.Inner.class_func.params': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'Sub.Inner.class_func.return': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.typed_getitem',
		'Sub.Inner.class_func.block': f'{_Sub}.class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
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
		'Sub.yields.yield': f'{_Sub_yields}.function_def_raw.typed_getitem',
		'Sub.yields.block': f'{_Sub_yields}.function_def_raw.block',
		'Sub.invoke_method.block': f'{_Sub_invoke_method}.function_def_raw.block',
		'Sub.decl_with_pop.block': f'{_Sub_decl_with_pop}.function_def_raw.block',
		'Sub.decl_locals.block': f'{_Sub_decl_locals}.function_def_raw.block',
		'Sub.decl_locals.closure.block': f'{_Sub_decl_locals}.function_def_raw.block.function_def.function_def_raw.block',
		'Sub.Base.return': f'{_Sub_Base}.function_def_raw.typed_var',
		'Sub.kw_params.block': f'{_Sub_kw_params}.function_def_raw.block',

		'TupleOps.unpack.block': f'{_TupleOps}.class_def_raw.block.function_def[0].function_def_raw.block',

		'CompOps.list_comp.block': f'{_CompOps}.class_def_raw.block.function_def[0].function_def_raw.block',

		'Nullable.returns.return': f'{_Nullable}.class_def_raw.block.function_def[1].function_def_raw.typed_or_expr',
		'Nullable.var_move.block': f'{_Nullable}.class_def_raw.block.function_def[2].function_def_raw.block',

		'GenericOps.new.block': f'{_GenericOps}.class_def_raw.block.function_def[2].function_def_raw.block',
		'GenericOps.cast.block': f'{_GenericOps}.class_def_raw.block.function_def[3].function_def_raw.block',

		'WithOps.file_load.block': f'{_WithOps}.class_def_raw.block.function_def.function_def_raw.block',
	}


def _ast(before: str, after: str) -> str:
	return ModuleDSN.local_joined(ASTMapping.aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.rogw.tranp.semantics.reflection.fixtures.test_symbol_db_xyz',
		'classes': 'rogw.tranp.compatible.libralies.classes',
		'typing': 'typing',
	}
	return ModuleDSN.full_joined(aliases[before], after)


class TestReflections(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.a'), list, False),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.closure.b'), list, True),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.a'), dict, False),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.closure.b'), dict, False),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d'), list, False),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d'), dict, False),  # XXX エイリアスはdictそのものではないが要検討
	])
	def test_is_a(self, fullyname: str, standard_type: type[Standards], expected: bool) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(fullyname)
		self.assertEqual(reflections.is_a(symbol, standard_type), expected)

	@data_provider([
		(ModuleDSN.full_joined(fixture_module_path, 'TypeAlias'), 'TypeAlias'),

		(ModuleDSN.full_joined(fixture_module_path, 'C'), 'C'),

		(ModuleDSN.full_joined(fixture_module_path, 'value'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),
		(ModuleDSN.full_joined(fixture_module_path, 'Base.base_str'), 'str'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner'), 'Inner'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner.value'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner.class_func'), 'class_func(Inner) -> dict<str, int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.numbers'), 'list<int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.__init__'), '__init__(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.__init__.self'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.local_ref'), 'local_ref(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.local_ref.self'), 'Sub'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.local_ref.value'), 'bool'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_ref'), 'member_ref(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_ref.self'), 'Sub'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_ref.a'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_ref.b'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_ref.c'), 'C'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_write'), 'member_write(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.member_write.self'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_ref'), 'param_ref(Sub, int) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_ref.self'), 'Sub'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_ref.param'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_ref'), 'list_ref(Sub, list<Sub>) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_ref.self'), 'Sub'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_ref.subs'), 'list<Sub>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.base_ref'), 'base_ref(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.base_ref.self'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.returns'), 'returns(Sub) -> str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.returns.self'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.invoke_method'), 'invoke_method(Sub) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.invoke_method.self'), 'Sub'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_with_pop.poped'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals'), 'decl_locals(Sub) -> int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.a'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.closure'), 'closure() -> list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_locals.closure.b'), 'list<int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.relay_access.s'), 'str'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.fill_list.n_x3'), 'list<int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_default.d'), 'DSI=dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_default.n'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_default.n2'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.param_default.keys'), 'list<str>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.kw_params.kwargs'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ns0'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ss0'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.s0'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ns_slice0'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ns_slice1'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ns_slice2'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.ss_slice'), 'list<str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.s_slice'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.indexer_access.dsn'), 'dict<str, int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.type_props.a'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.type_props.b'), 'type<Sub>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.type_props.c'), 'str'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_expand.a'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_expand.b'), 'list<list<int>>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.list_expand.c'), 'list<int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.dict_expand.a'), 'dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.dict_expand.b'), 'dict<str, dict<str, int>>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.tuple_arg.a'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.tuple_arg.b'), 'bool'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_tuple.a'), 'tuple<int, str, bool>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_tuple.b'), 'tuple<int, int, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.decl_tuple.c'), 'tuple<str, str, str>'),

		(ModuleDSN.full_joined(fixture_module_path, 'Sub.imported_inner_type_ref.b'), 'AA=A'),
		(ModuleDSN.full_joined(fixture_module_path, 'Sub.imported_inner_type_ref.a'), 'A'),

		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.unary.n_neg'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.unary.n_not'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.n'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.nb0'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.nb1'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.fn0'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.fn1'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.fn2'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.fb0'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.fb1'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.result'), 'float'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.l_in'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.l_not_in'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.n_is'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.binary.n_is_not'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.tenary.n'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.tenary.s'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'CalcOps.tenary.s_or_null'), 'Union<str, None>'),

		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func'), 'func(AliasOps, C2=C) -> None'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.z2'), 'C2=C'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d'), 'DSI=dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d_in_v'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d2'), 'DSI2=dict<str, DSI=dict<str, int>>'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d2_in_dsi'), 'DSI=dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.d2_in_dsi_in_v'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.z2_in_x'), 'A'),
		(ModuleDSN.full_joined(fixture_module_path, 'AliasOps.func.new_z2_in_x'), 'A'),

		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.t'), 'tuple<int, str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.t0'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.t1'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.tu'), 'Union<int, str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.a'), 'str'),  # XXX Pythonのシンタックス上は不正。一旦保留
		(ModuleDSN.full_joined(fixture_module_path, 'TupleOps.assign.b'), 'int'),  # XXX 〃

		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.list_comp.values0'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.list_comp.values1'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.list_comp.values2'), 'list<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.list_comp.strs'), 'list<str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.list_comp.value'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.dict_comp.kvs0'), 'dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.dict_comp.kvs1'), 'dict<str, int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'CompOps.dict_comp.kvs2'), 'dict<str, int>'),

		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.Values'), 'Values'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.Values.A'), 'int'),  # Enumの定数値を直接参照するとEnum型ではなく、オリジナルの型になる ※情報を損なわないようにするため
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.Values.B'), 'int'),  # 〃
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.cls_assign.a'), 'Values'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.cls_assign.d'), 'dict<Values, str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.cls_assign.da'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.assign.a'), 'Values'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.assign.d'), 'dict<Values, str>'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.assign.da'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.cast.e'), 'Values'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.cast.n'), 'int'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.comparison.a'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.comparison.b'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.comparison.c'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.comparison.d'), 'bool'),
		(ModuleDSN.full_joined(fixture_module_path, 'EnumOps.calc.a'), 'Values'),

		(ModuleDSN.full_joined(fixture_module_path, 'Nullable.params.base'), 'Union<Base, None>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Nullable.accessible.sub'), 'Union<Sub, None>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Nullable.accessible.subs'), 'Union<list<Sub>, None>'),
		(ModuleDSN.full_joined(fixture_module_path, 'Nullable.accessible.s'), 'str'),
		(ModuleDSN.full_joined(fixture_module_path, 'Nullable.accessible.n'), 'int'),

		(ModuleDSN.full_joined(fixture_module_path, 'GenericOps.temporal.a'), 'T'),
		(ModuleDSN.full_joined(fixture_module_path, 'GenericOps.new.a'), 'GenericOps<int>'),
		(ModuleDSN.full_joined(fixture_module_path, 'GenericOps.cast.b'), 'GenericOps<Base>'),

		(ModuleDSN.full_joined(fixture_module_path, 'WithOps.file_load.dir'), 'str'),
	])
	def test_from_fullyname(self, fullyname: str, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(fullyname)
		self.assertEqual(str(symbol), expected)

	@data_provider([
		(int, _mod('classes', int.__name__)),
		(float, _mod('classes', float.__name__)),
		(str, _mod('classes', str.__name__)),
		(bool, _mod('classes', bool.__name__)),
		(tuple, _mod('classes', tuple.__name__)),
		(list, _mod('classes', list.__name__)),
		(dict, _mod('classes', dict.__name__)),
		(classes.Unknown, _mod('classes', classes.Unknown.__name__)),
		(classes.Union, _mod('classes', 'Union')),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_standard(self, standard_type: type[Standards] | None, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		self.assertEqual(reflections.type_of_standard(standard_type).types.fullyname, expected)

	@data_provider([
		(_ast(ModuleDSN.full_joined(fixture_module_path, 'import.xyz'), 'import_as_names.import_as_name[1]'), _mod('xyz', 'C'), 'C'),
		(_ast(ModuleDSN.full_joined(fixture_module_path, 'value'), 'assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast(ModuleDSN.full_joined(fixture_module_path, 'value'), 'typed_var'), _mod('classes', 'int'), 'int'),
		(_ast(ModuleDSN.full_joined(fixture_module_path, 'value'), 'number'), _mod('classes', 'int'), 'int'),

		(_ast('Base', ''), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),
		(_ast('Base', 'class_def_raw.name'), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),

		(_ast('Base.__init__.params', 'paramvalue.typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),
		(_ast('Base.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Base.__init__.block', 'anno_assign.assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'anno_assign.var'), _mod('classes', 'str'), 'str'),
		(_ast('Base.__init__.block', 'comment_stmt'), _mod('classes', 'Unknown'), 'Unknown'),

		(_ast('Sub', ''), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub', 'class_def_raw.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub', 'class_def_raw.inherit_arguments.typed_argvalue.typed_var'), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),

		(_ast('Sub.Inner', ''), ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner'), 'Inner'),
		(_ast('Sub.Inner.block', 'class_var_assign.assign_namelist.var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.Inner.block', 'class_var_assign.typed_var'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.Inner.block', 'class_var_assign.string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.Inner.class_func', ''), ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner.class_func'), 'class_func(Inner) -> dict<str, int>'),
		(_ast('Sub.Inner.class_func.params', 'paramvalue.typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub.Inner'), 'Inner'),
		(_ast('Sub.Inner.class_func.return', ''), _mod('classes', 'dict'), 'dict<str, int>'),
		(_ast('Sub.Inner.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), 'dict<str, int>'),

		(_ast('Sub.__init__.params', 'paramvalue.typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub.__init__.return', ''), _mod('classes', 'None'), 'None'),
		(_ast('Sub.__init__.block', 'funccall'), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),
		(_ast('Sub.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), 'super'),
		(_ast('Sub.__init__.block', 'anno_assign[1]'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign[1].assign_namelist.getattr'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign[1].typed_getitem'), _mod('classes', 'list'), 'list<int>'),
		(_ast('Sub.__init__.block', 'anno_assign[1].list'), _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		(_ast('Sub.first_number.block', 'return_stmt'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.local_ref.params', 'paramvalue.typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub.local_ref.block', 'assign'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.block', 'funccall.var'), _mod('classes', 'print'), 'print(Any) -> None'),
		(_ast('Sub.local_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'bool'), 'bool'),
		(_ast('Sub.local_ref.return', ''), _mod('classes', 'None'), 'None'),

		(_ast('Sub.member_write.block', 'assign[0].assign_namelist.getattr'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[0].number'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.member_write.block', 'assign[1].assign_namelist.getattr'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.member_write.block', 'assign[1].string'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.param_ref.params', 'paramvalue[0].typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub.param_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.param_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.list_ref.params', 'paramvalue[0].typedparam.name'), ModuleDSN.full_joined(fixture_module_path, 'Sub'), 'Sub'),
		(_ast('Sub.list_ref.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), 'list<Sub>'),
		(_ast('Sub.list_ref.block', 'funccall[0].arguments.argvalue'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.list_ref.block', 'funccall[1].arguments.argvalue'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.base_ref.block', 'funccall.arguments.argvalue'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.returns.return', ''), _mod('classes', 'str'), 'str'),
		(_ast('Sub.returns.block', 'return_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.yields.yield', ''), _mod('typing', 'Iterator'), 'Iterator<str>'),
		(_ast('Sub.yields.block', 'yield_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('Sub.invoke_method.block', 'funccall.getattr'), ModuleDSN.full_joined(fixture_module_path, 'Sub.invoke_method'), 'invoke_method(Sub) -> None'),

		(_ast('Sub.decl_with_pop.block', 'assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_with_pop.block', 'assign.funccall'), _mod('classes', 'int'), 'int'),

		(_ast('Sub.decl_locals.block', 'if_stmt[1].if_clause.block.assign[0].assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_locals.closure.block', 'assign.assign_namelist.var'), _mod('classes', 'list'), 'list<int>'),

		(_ast('Sub.decl_locals.block', 'if_stmt[1].if_clause.block.for_stmt.for_namelist.name'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.decl_locals.block', 'if_stmt[1].if_clause.block.for_stmt.block.try_stmt.except_clauses.except_clause.name'), _mod('classes', 'Exception'), 'Exception'),

		(_ast('Sub.Base.return', ''), ModuleDSN.full_joined(fixture_module_path, 'Base'), 'Base'),

		(_ast('Sub.kw_params.block', 'assign'), _mod('classes', 'str'), 'str'),
		(_ast('Sub.kw_params.block', 'assign.funccall.arguments.argvalue[0]'), _mod('classes', 'int'), 'int'),
		(_ast('Sub.kw_params.block', 'assign.funccall.arguments.argvalue[1]'), _mod('classes', 'int'), 'int'),

		(_ast('TupleOps.unpack.block', 'for_stmt[0].for_namelist.name[0]'), _mod('classes', 'str'), 'str'),
		(_ast('TupleOps.unpack.block', 'for_stmt[0].for_namelist.name[1]'), _mod('classes', 'int'), 'int'),
		(_ast('TupleOps.unpack.block', 'for_stmt[1].for_namelist.name'), _mod('classes', 'int'), 'int'),
		(_ast('TupleOps.unpack.block', 'for_stmt[2].for_namelist.name'), _mod('classes', 'str'), 'str'),
		(_ast('TupleOps.unpack.block', 'for_stmt[3].for_namelist.name'), _mod('classes', 'tuple'), 'tuple<str, int>'),

		(_ast('TupleOps.unpack.block', 'for_stmt[5].for_namelist.name[0]'), _mod('classes', 'str'), 'str'),
		(_ast('TupleOps.unpack.block', 'for_stmt[5].for_namelist.name[1]'), ModuleDSN.full_joined(fixture_module_path, 'DSI'), 'DSI=dict<str, int>'),
		(_ast('TupleOps.unpack.block', 'for_stmt[6].for_namelist.name'), ModuleDSN.full_joined(fixture_module_path, 'DSI'), 'DSI=dict<str, int>'),
		(_ast('TupleOps.unpack.block', 'for_stmt[7].for_namelist.name'), _mod('classes', 'str'), 'str'),
		(_ast('TupleOps.unpack.block', 'for_stmt[8].for_namelist.name'), _mod('classes', 'tuple'), 'tuple<str, DSI=dict<str, int>>'),

		(_ast('CompOps.list_comp.block', 'aug_assign.assign_namelist.var'), _mod('classes', 'int'), 'int'),
		(_ast('CompOps.list_comp.block', 'aug_assign.getitem'), _mod('classes', 'float'), 'float'),

		(_ast('Nullable.returns.return', ''), _mod('classes', 'Union'), 'Union<Base, None>'),
		(_ast('Nullable.var_move.block', 'if_stmt.if_clause.block.return_stmt'), _mod('classes', 'str'), 'str'),

		(_ast('GenericOps.new.block', 'assign.funccall'), ModuleDSN.full_joined(fixture_module_path, 'GenericOps'), 'GenericOps<int>'),
		(_ast('GenericOps.cast.block', 'assign.funccall.arguments.argvalue[0]'), _mod('classes', 'type'), 'type<GenericOps<Base>>'),

		(_ast('WithOps.file_load.block', 'with_stmt.with_items.with_item'), _mod('typing', 'IO'), 'IO'),
		(_ast('WithOps.file_load.block', 'with_stmt.block.assign'), _mod('classes', 'dict'), 'dict<str, Any>'),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		node = self.fixture.shared_nodes_by(full_path)
		symbol = reflections.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(str(symbol), attrs_expected)
