from unittest import TestCase

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.lang.annotation import override
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


def _mod(before: str, after: str) -> str:
	aliases = {
		'classes': 'rogw.tranp.compatible.libralies.classes',
		'typing': 'typing',
		'xyz': 'tests.unit.rogw.tranp.semantics.reflection.fixtures.test_db_xyz',
		'__main__': 'tests.unit.rogw.tranp.semantics.fixtures.test_reflections',
	}
	return ModuleDSN.full_joined(aliases[before], after)


class TestReflections(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@override
	def setUp(self) -> None:
		super().setUp()
		# XXX モジュールをロードすることでシンボルテーブルが完成するため、必ず事前に実施
		self.fixture.shared_module

	@data_provider([
		('Sub.decl_locals.a', list, False),
		('Sub.decl_locals.closure.b', list, True),
		('Sub.decl_locals.a', dict, False),
		('Sub.decl_locals.closure.b', dict, False),
		('AliasOps.func.d', list, False),
		('AliasOps.func.d', dict, False),  # XXX エイリアスはdictそのものではないが要検討
	])
	def test_type_is(self, local_path: str, standard_type: type[Standards], expected: bool) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path))
		self.assertEqual(reflections.type_is(symbol.types, standard_type), expected)

	@data_provider([
		('TypeAlias', 'TypeAlias'),

		('C', 'C'),

		('value', 'int'),

		('Base', 'Base'),
		('Base.base_str', 'str'),

		('Base.return_self', 'return_self(Self) -> Self'),
		('Base.return_self.base', 'Base'),

		('Sub', 'Sub'),

		('Sub.Inner', 'Inner'),
		('Sub.Inner.value', 'str'),
		('Sub.Inner.class_func', 'class_func(type<Inner>) -> dict<str, int>'),

		('Sub.numbers', 'list<int>'),

		('Sub.__init__', '__init__(Sub) -> None'),
		('Sub.__init__.self', 'Sub'),

		('Sub.local_ref', 'local_ref(Sub) -> None'),
		('Sub.local_ref.self', 'Sub'),
		('Sub.local_ref.value', 'bool'),

		('Sub.member_ref', 'member_ref(Self) -> None'),
		('Sub.member_ref.self', 'Self'),
		('Sub.member_ref.a', 'list<int>'),
		('Sub.member_ref.b', 'int'),
		('Sub.member_ref.c', 'C'),
		('Sub.member_ref.sub', 'Sub'),

		('Sub.member_write', 'member_write(Sub) -> None'),
		('Sub.member_write.self', 'Sub'),

		('Sub.param_ref', 'param_ref(Sub, int) -> None'),
		('Sub.param_ref.self', 'Sub'),
		('Sub.param_ref.param', 'int'),

		('Sub.list_ref', 'list_ref(Sub, list<Sub>) -> None'),
		('Sub.list_ref.self', 'Sub'),
		('Sub.list_ref.subs', 'list<Sub>'),

		('Sub.base_ref', 'base_ref(Sub) -> None'),
		('Sub.base_ref.self', 'Sub'),

		('Sub.returns', 'returns(Sub) -> str'),
		('Sub.returns.self', 'Sub'),

		('Sub.invoke_method', 'invoke_method(Sub) -> None'),
		('Sub.invoke_method.self', 'Sub'),

		('Sub.decl_with_pop.poped', 'int'),

		('Sub.decl_locals', 'decl_locals(Sub) -> int'),
		('Sub.decl_locals.a', 'int'),
		('Sub.decl_locals.closure', 'closure() -> list<int>'),
		('Sub.decl_locals.closure.b', 'list<int>'),

		('Sub.relay_access.s', 'str'),

		('Sub.fill_list.n_x3', 'list<int>'),

		('Sub.param_default.d', 'DSI=dict<str, int>'),
		('Sub.param_default.n', 'int'),
		('Sub.param_default.n2', 'int'),
		('Sub.param_default.keys', 'list<str>'),

		('Sub.kw_params.kwargs', 'int'),

		('Sub.indexer_access.ns0', 'int'),
		('Sub.indexer_access.ss0', 'str'),
		('Sub.indexer_access.s0', 'str'),
		('Sub.indexer_access.ns_slice0', 'list<int>'),
		('Sub.indexer_access.ns_slice1', 'list<int>'),
		('Sub.indexer_access.ns_slice2', 'list<int>'),
		('Sub.indexer_access.ss_slice', 'list<str>'),
		('Sub.indexer_access.s_slice', 'str'),
		('Sub.indexer_access.dsn', 'dict<str, int>'),

		('Sub.type_props.a', 'str'),
		('Sub.type_props.b', 'type<Sub>'),
		('Sub.type_props.c', 'str'),

		('Sub.list_expand.a', 'list<int>'),
		('Sub.list_expand.b', 'list<list<int>>'),
		('Sub.list_expand.c', 'list<int>'),

		('Sub.dict_expand.a', 'dict<str, int>'),
		('Sub.dict_expand.b', 'dict<str, dict<str, int>>'),

		('Sub.tuple_arg.a', 'bool'),
		('Sub.tuple_arg.b', 'bool'),

		('Sub.decl_tuple.a', 'tuple<int, str, bool>'),
		('Sub.decl_tuple.b', 'tuple<int, int, int>'),
		('Sub.decl_tuple.c', 'tuple<str, str, str>'),

		('Sub.imported_inner_type_ref.b', 'AA=A'),
		('Sub.imported_inner_type_ref.a', 'A'),

		('CalcOps.unary.n_neg', 'int'),
		('CalcOps.unary.n_not', 'bool'),
		('CalcOps.binary.n', 'int'),
		('CalcOps.binary.nb0', 'int'),
		('CalcOps.binary.nb1', 'int'),
		('CalcOps.binary.fn0', 'float'),
		('CalcOps.binary.fn1', 'float'),
		('CalcOps.binary.fn2', 'float'),
		('CalcOps.binary.fb0', 'float'),
		('CalcOps.binary.fb1', 'float'),
		('CalcOps.binary.result', 'float'),
		('CalcOps.binary.l_in', 'bool'),
		('CalcOps.binary.l_not_in', 'bool'),
		('CalcOps.binary.n_is', 'bool'),
		('CalcOps.binary.n_is_not', 'bool'),
		('CalcOps.tenary.n', 'int'),
		('CalcOps.tenary.s', 'str'),
		('CalcOps.tenary.s_or_null', 'Union<str, None>'),

		('AliasOps.func', 'func(AliasOps, C2=C) -> None'),
		('AliasOps.func.z2', 'C2=C'),
		('AliasOps.func.d', 'DSI=dict<str, int>'),
		('AliasOps.func.d_in_v', 'int'),
		('AliasOps.func.d2', 'DSI2=dict<str, DSI=dict<str, int>>'),
		('AliasOps.func.d2_in_dsi', 'DSI=dict<str, int>'),
		('AliasOps.func.d2_in_dsi_in_v', 'int'),
		('AliasOps.func.z2_in_x', 'A'),
		('AliasOps.func.new_z2_in_x', 'A'),

		('TupleOps.assign.t', 'tuple<int, str>'),
		('TupleOps.assign.t0', 'int'),
		('TupleOps.assign.t1', 'str'),
		('TupleOps.assign.tu', 'Union<int, str>'),
		('TupleOps.assign.a', 'str'),  # XXX Pythonのシンタックス上は不正。一旦保留
		('TupleOps.assign.b', 'int'),  # XXX 〃

		('CompOps.list_comp.values0', 'list<int>'),
		('CompOps.list_comp.values1', 'list<int>'),
		('CompOps.list_comp.values2', 'list<int>'),
		('CompOps.list_comp.strs', 'list<str>'),
		('CompOps.list_comp.value', 'int'),

		('CompOps.dict_comp.kvs0', 'dict<str, int>'),
		('CompOps.dict_comp.kvs1', 'dict<str, int>'),
		('CompOps.dict_comp.kvs2', 'dict<str, int>'),

		('EnumOps.Values', 'Values'),
		('EnumOps.Values.A', 'int'),  # Enumの定数値を直接参照するとEnum型ではなく、オリジナルの型になる ※情報を損なわないようにするため
		('EnumOps.Values.B', 'int'),  # 〃
		('EnumOps.cls_assign.a', 'Values'),
		('EnumOps.cls_assign.d', 'dict<Values, str>'),
		('EnumOps.cls_assign.da', 'str'),
		('EnumOps.assign.a', 'Values'),
		('EnumOps.assign.d', 'dict<Values, str>'),
		('EnumOps.assign.da', 'str'),
		('EnumOps.cast.e', 'Values'),
		('EnumOps.cast.n', 'int'),
		('EnumOps.comparison.a', 'bool'),
		('EnumOps.comparison.b', 'bool'),
		('EnumOps.comparison.c', 'bool'),
		('EnumOps.comparison.d', 'bool'),
		('EnumOps.calc.a', 'Values'),

		('Nullable.params.base', 'Union<Base, None>'),
		('Nullable.accessible.sub', 'Union<Sub, None>'),
		('Nullable.accessible.subs', 'Union<list<Sub>, None>'),
		('Nullable.accessible.s', 'str'),
		('Nullable.accessible.n', 'int'),

		('GenericOps.temporal.a', 'T'),
		('GenericOps.new.a', 'GenericOps<int>'),
		('GenericOps.cast.b', 'GenericOps<Base>'),

		('WithOps.file_load.dir', 'str'),
	])
	def test_from_fullyname(self, local_path: str, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path))
		self.assertEqual(ClassShorthandNaming.domain_name_for_debug(symbol), expected)

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
		self.assertEqual(reflections.from_standard(standard_type).types.fullyname, expected)

	@data_provider([
		('C', '', _mod('xyz', 'C'), 'C'),
		('value', '', _mod('classes', 'int'), 'int'),

		('Base', '', _mod('classes', 'type'), 'type<Base>'),
		('Base', 'class_def_raw.name', _mod('classes', 'type'), 'type<Base>'),

		('Base.__init__', 'function_def_raw.parameters.paramvalue.typedparam.name', _mod('__main__', 'Base'), 'Base'),
		('Base.__init__', 'function_def_raw.typed_none', _mod('classes', 'None'), 'None'),
		('Base.__init__', 'function_def_raw.block.anno_assign.assign_namelist.getattr', _mod('classes', 'str'), 'str'),
		('Base.__init__', 'function_def_raw.block.anno_assign.typed_var', _mod('classes', 'str'), 'str'),
		('Base.__init__', 'function_def_raw.block.anno_assign.var', _mod('classes', 'str'), 'str'),
		('Base.__init__', 'function_def_raw.block.comment_stmt', _mod('classes', 'Unknown'), 'Unknown'),

		('Sub', '', _mod('classes', 'type'), 'type<Sub>'),
		('Sub', 'class_def_raw.name', _mod('classes', 'type'), 'type<Sub>'),
		('Sub', 'class_def_raw.inherit_arguments.typed_argvalue.typed_var', _mod('__main__', 'Base'), 'Base'),

		('Sub.Inner', '', _mod('classes', 'type'), 'type<Inner>'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.assign_namelist.var', _mod('classes', 'str'), 'str'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.typed_var', _mod('classes', 'str'), 'str'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.string', _mod('classes', 'str'), 'str'),

		('Sub.Inner.class_func', '', _mod('__main__', 'Sub.Inner.class_func'), 'class_func(type<Inner>) -> dict<str, int>'),
		('Sub.Inner.class_func', 'function_def_raw.parameters.paramvalue.typedparam.name', _mod('classes', 'type'), 'type<Inner>'),
		('Sub.Inner.class_func', 'function_def_raw.typed_getitem', _mod('classes', 'dict'), 'dict<str, int>'),
		('Sub.Inner.class_func', 'function_def_raw.block.return_stmt.dict.key_value.getattr.var', _mod('classes', 'type'), 'type<Inner>'),
		('Sub.Inner.class_func', 'function_def_raw.block.return_stmt.dict', _mod('classes', 'dict'), 'dict<str, int>'),

		('Sub.__init__', 'function_def_raw.parameters.paramvalue.typedparam.name', _mod('__main__', 'Sub'), 'Sub'),
		('Sub.__init__', 'function_def_raw.typed_none', _mod('classes', 'None'), 'None'),
		('Sub.__init__', 'function_def_raw.block.funccall', _mod('__main__', 'Base'), 'Base'),
		('Sub.__init__', 'function_def_raw.block.funccall.getattr.funccall.var', _mod('classes', 'super'), 'super() -> Any'),
		('Sub.__init__', 'function_def_raw.block.anno_assign[1]', _mod('classes', 'list'), 'list<int>'),
		('Sub.__init__', 'function_def_raw.block.anno_assign[1].assign_namelist.getattr', _mod('classes', 'list'), 'list<int>'),
		('Sub.__init__', 'function_def_raw.block.anno_assign[1].typed_getitem', _mod('classes', 'list'), 'list<int>'),
		('Sub.__init__', 'function_def_raw.block.anno_assign[1].list', _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		('Sub.first_number', 'function_def_raw.typed_var', _mod('classes', 'int'), 'int'),

		('Sub.local_ref', 'function_def_raw.parameters.paramvalue.typedparam.name', _mod('__main__', 'Sub'), 'Sub'),
		('Sub.local_ref', 'function_def_raw.block.assign', _mod('classes', 'bool'), 'bool'),
		('Sub.local_ref', 'function_def_raw.block.funccall.var', _mod('classes', 'print'), 'print(Any) -> None'),
		('Sub.local_ref', 'function_def_raw.block.funccall.arguments.argvalue', _mod('classes', 'bool'), 'bool'),
		('Sub.local_ref', 'function_def_raw.typed_none', _mod('classes', 'None'), 'None'),

		('Sub.member_write', 'function_def_raw.block.assign[0].assign_namelist.getattr', _mod('classes', 'int'), 'int'),
		('Sub.member_write', 'function_def_raw.block.assign[0].number', _mod('classes', 'int'), 'int'),
		('Sub.member_write', 'function_def_raw.block.assign[1].assign_namelist.getattr', _mod('classes', 'str'), 'str'),
		('Sub.member_write', 'function_def_raw.block.assign[1].string', _mod('classes', 'str'), 'str'),

		('Sub.param_ref', 'function_def_raw.parameters.paramvalue[0].typedparam.name', _mod('__main__', 'Sub'), 'Sub'),
		('Sub.param_ref', 'function_def_raw.parameters.paramvalue[1].typedparam.name', _mod('classes', 'int'), 'int'),
		('Sub.param_ref', 'function_def_raw.block.funccall.arguments.argvalue', _mod('classes', 'int'), 'int'),

		('Sub.list_ref', 'function_def_raw.parameters.paramvalue[0].typedparam.name', _mod('__main__', 'Sub'), 'Sub'),
		('Sub.list_ref', 'function_def_raw.parameters.paramvalue[1].typedparam.name', _mod('classes', 'list'), 'list<Sub>'),
		('Sub.list_ref', 'function_def_raw.block.funccall[0].arguments.argvalue', _mod('classes', 'int'), 'int'),
		('Sub.list_ref', 'function_def_raw.block.funccall[1].arguments.argvalue', _mod('classes', 'list'), 'list<int>'),

		('Sub.base_ref', 'function_def_raw.block.funccall.arguments.argvalue', _mod('classes', 'str'), 'str'),

		('Sub.returns', 'function_def_raw.typed_var', _mod('classes', 'str'), 'str'),
		('Sub.returns', 'function_def_raw.typed_var', _mod('classes', 'str'), 'str'),

		('Sub.yields', 'function_def_raw.typed_getitem', _mod('typing', 'Iterator'), 'Iterator<str>'),
		('Sub.yields', 'function_def_raw.block.yield_stmt', _mod('classes', 'str'), 'str'),

		('Sub.invoke_method', 'function_def_raw.block.funccall.getattr', _mod('__main__', 'Sub.invoke_method'), 'invoke_method(Sub) -> None'),

		('Sub.decl_with_pop', 'function_def_raw.block.assign.assign_namelist.var', _mod('classes', 'int'), 'int'),
		('Sub.decl_with_pop', 'function_def_raw.block.assign.funccall', _mod('classes', 'int'), 'int'),

		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.assign[0].assign_namelist.var', _mod('classes', 'int'), 'int'),
		('Sub.decl_locals.closure', 'function_def_raw.block.assign.assign_namelist.var', _mod('classes', 'list'), 'list<int>'),

		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.for_stmt.for_namelist.name', _mod('classes', 'int'), 'int'),
		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.for_stmt.block.try_stmt.except_clauses.except_clause.name', _mod('classes', 'Exception'), 'Exception'),

		('Sub.Base', 'function_def_raw.typed_var', _mod('__main__', 'Base'), 'Base'),

		('Sub.kw_params', 'function_def_raw.block.assign', _mod('classes', 'str'), 'str'),
		('Sub.kw_params', 'function_def_raw.block.assign.funccall.arguments.argvalue[0]', _mod('classes', 'int'), 'int'),
		('Sub.kw_params', 'function_def_raw.block.assign.funccall.arguments.argvalue[1]', _mod('classes', 'int'), 'int'),

		('TupleOps.unpack', 'function_def_raw.block.for_stmt[0].for_namelist.name[0]', _mod('classes', 'str'), 'str'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[0].for_namelist.name[1]', _mod('classes', 'int'), 'int'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[1].for_namelist.name', _mod('classes', 'int'), 'int'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[2].for_namelist.name', _mod('classes', 'str'), 'str'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[3].for_namelist.name', _mod('classes', 'str'), 'str'),

		('TupleOps.unpack', 'function_def_raw.block.for_stmt[5].for_namelist.name[0]', _mod('classes', 'str'), 'str'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[5].for_namelist.name[1]', _mod('__main__', 'DSI'), 'DSI=dict<str, int>'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[6].for_namelist.name', _mod('__main__', 'DSI'), 'DSI=dict<str, int>'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[7].for_namelist.name', _mod('classes', 'str'), 'str'),
		('TupleOps.unpack', 'function_def_raw.block.for_stmt[8].for_namelist.name', _mod('classes', 'str'), 'str'),

		('CompOps.list_comp', 'function_def_raw.block.aug_assign.assign_namelist.var', _mod('classes', 'int'), 'int'),
		('CompOps.list_comp', 'function_def_raw.block.aug_assign.getitem', _mod('classes', 'float'), 'float'),

		('Nullable.returns', 'function_def_raw.typed_or_expr', _mod('classes', 'Union'), 'Union<Base, None>'),
		('Nullable.var_move', 'function_def_raw.block.if_stmt.if_clause.block.return_stmt', _mod('classes', 'str'), 'str'),

		('GenericOps.new', 'function_def_raw.block.assign.funccall', _mod('__main__', 'GenericOps'), 'GenericOps<int>'),
		('GenericOps.cast', 'function_def_raw.block.assign.funccall.arguments.argvalue[0]', _mod('classes', 'type'), 'type<GenericOps<Base>>'),

		('WithOps.file_load', 'function_def_raw.block.with_stmt.with_items.with_item', _mod('typing', 'IO'), 'IO'),
		('WithOps.file_load', 'function_def_raw.block.with_stmt.block.assign', _mod('classes', 'dict'), 'dict<str, Any>'),
	])
	def test_type_of(self, local_path: str, offset_path: str, expected: str, attrs_expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		via = reflections.from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path))
		full_path = ModuleDSN.local_joined(via.node.full_path, offset_path)
		node = self.fixture.shared_module.entrypoint.whole_by(full_path)
		symbol = reflections.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(ClassShorthandNaming.domain_name_for_debug(symbol), attrs_expected)

	# XXX 速度面で課題があるため一旦廃止
	# @data_provider([
	# 	# Import
	# 	('from typing import TypeAlias', 'file_input.import_stmt.import_as_names.import_as_name.name', 'TypeAlias'),
	# 	# Class
	# 	('class A: ...', 'file_input.class_def', 'type<A>'),
	# 	('class A: ...\nclass B(A): ...', 'file_input.class_def[1]', 'type<B>'),
	# 	('class A:\n\tclass AA: ...', 'file_input.class_def.class_def_raw.block.class_def', 'type<AA>'),
	# 	# Declable - LocalVar
	# 	('a: int = 0', 'file_input.anno_assign', 'int'),
	# 	# Declable - SelfVar
	# 	('class A:\n\tself_s: str\n\tdef __init__(self) -> None:\n\t\tself.self_s: str = ""', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign', 'str'),
	# 	('class A:\n\tself_l: \'list[A]\'\n\tdef __init__(self) -> None:\n\t\tself.self_l: list[A] = []', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign', 'list<A>'),
	# 	# Declable - ClassVar
	# 	('from typing import ClassVar\nclass A:\n\tcls_n: ClassVar[int] = 0\n\t@classmethod\n\tdef cls_method(cls) -> None:\n\t\tprint(cls.cls_n)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.getattr', 'int'),
	# 	# Declable - Parameter
	# 	('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', 'A'),
	# 	('class A:\n\t@classmethod\n\tdef cls_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', 'type<A>'),
	# 	# Reference - Relay
	# 	('class A:\n\tself_s: str\n\tdef __init__(self) -> None:\n\t\tself.self_s: str = ""\n\t\tprint(self.self_s)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.getattr', 'str'),
	# 	('class A: ...\nclass B:\n\tself_a: A\n\tdef __init__(self) -> None:\n\t\tself.self_a: A = A()\n\t\tprint(self.self_a)', 'file_input.class_def[1].class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.getattr', 'A'),
	# 	# Reference - Var
	# 	('class A:\n\tdef __init__(self) -> None: print(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', 'A'),
	# 	('def func(b: bool) -> None: print(b)', 'file_input.function_def.function_def_raw.block.funccall.arguments.argvalue.var', 'bool'),
	# 	('def func() -> None:\n\tn = 0\n\tprint(n)', 'file_input.function_def.function_def_raw.block.funccall.arguments.argvalue.var', 'int'),
	# 	# Function - Method
	# 	('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', '__init__(A) -> None'),
	# 	('class A:\n\tclass AA:\n\t\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.function_def', '__init__(AA) -> None'),
	# 	('class A:\n\t@classmethod\n\tdef cls_method(cls) -> dict[str, int]: ...', 'file_input.class_def.class_def_raw.block.function_def', 'cls_method(type<A>) -> dict<str, int>'),
	# 	('class A:\n\tclass AA:\n\t\t@classmethod\n\t\tdef cls_method(cls) -> list[int]: ...', 'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.function_def', 'cls_method(type<AA>) -> list<int>'),
	# ])
	# def test_type_of2(self, source_code: str, full_path: str, expected: str) -> None:
	# 	reflections = self.fixture.get(Reflections)
	# 	node = self.fixture.custom_module(source_code).entrypoint.whole_by(full_path)
	# 	symbol = reflections.type_of(node)
	# 	self.assertEqual(ClassShorthandNaming.domain_name_for_debug(symbol), expected)
