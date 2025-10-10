from collections.abc import Callable
from typing import override
from unittest import TestCase

from rogw.tranp.compatible.python.types import Standards, Union, Unknown
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflection.helper.naming import ClassShorthandNaming
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


def _mod(before: str, after: str) -> str:
	aliases = {
		'classes': 'rogw.tranp.compatible.libralies.classes',
		'type': 'rogw.tranp.compatible.libralies.type',
		'typing': 'typing',
		'collections': 'collections.abc',
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

	def test_get_object(self) -> None:
		reflections = self.fixture.get(Reflections)
		self.assertEqual(reflections.get_object().types.fullyname, _mod('classes', 'object'))

	@data_provider([
		(bool, _mod('classes', bool.__name__)),
		(int, _mod('classes', int.__name__)),
		(float, _mod('classes', float.__name__)),
		(str, _mod('classes', str.__name__)),
		(list, _mod('classes', list.__name__)),
		(dict, _mod('classes', dict.__name__)),
		(tuple, _mod('classes', tuple.__name__)),
		(type, _mod('type', type.__name__)),
		(Callable, _mod('collections', Callable.__name__)),
		(Union, _mod('typing', Union.__name__)),
		(Unknown, _mod('classes', Unknown.__name__)),
		(None, _mod('classes', 'None')),
	])
	def test_from_standard(self, standard_type: type[Standards] | None, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		self.assertEqual(reflections.from_standard(standard_type).types.fullyname, expected)

	@data_provider([
		 # XXX DeclClassParamはClassRefより間接的に参照され、on_class_refによってtype<Class>にラップされる
		 # XXX DeclClassParamをラップせずとも害がなく、ラップするとかえって複雑さが増してしまうためこのままとしておく
		('Sub.Inner.class_func.cls', 'Inner'),
	])
	def test_from_fullyname(self, local_path: str, expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		symbol = reflections.from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path))
		self.assertEqual(symbol.pretty, expected)

	@data_provider([
		('Base', '', _mod('type', 'type'), 'type<Base>'),
		('Base', 'class_def_raw.name', _mod('type', 'type'), 'type<Base>'),

		('Base.__init__', 'function_def_raw.block.assign.var', _mod('classes', 'str'), 'str'),
		('Base.__init__', 'function_def_raw.block.comment_stmt', _mod('classes', 'Unknown'), 'Unknown'),

		('Sub', '', _mod('type', 'type'), 'type<Sub>'),
		('Sub', 'class_def_raw.name', _mod('type', 'type'), 'type<Sub>'),
		('Sub', 'class_def_raw.inherit_arguments.typed_argvalue.typed_var', _mod('__main__', 'Base'), 'Base'),

		('Sub.Inner', '', _mod('type', 'type'), 'type<Inner>'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.assign_namelist.var', _mod('classes', 'str'), 'str'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.typed_var', _mod('classes', 'str'), 'str'),
		('Sub.Inner', 'class_def_raw.block.class_var_assign.string', _mod('classes', 'str'), 'str'),

		('Sub.Inner.class_func', 'function_def_raw.block.return_stmt.dict.key_value.getattr.var', _mod('type', 'type'), 'type<Inner>'),
		('Sub.Inner.class_func', 'function_def_raw.block.return_stmt.dict', _mod('classes', 'dict'), 'dict<str, int>'),

		('Sub.__init__', 'function_def_raw.block.funccall', _mod('__main__', 'Base'), 'Base'),
		('Sub.__init__', 'function_def_raw.block.funccall.getattr.funccall.var', _mod('classes', 'super'), 'super() -> Any'),
		('Sub.__init__', 'function_def_raw.block.assign.list', _mod('classes', 'list'), 'list<Unknown>'),  # XXX 空のリストは型を補完できないためlist<Unknown>になる

		('Sub.local_ref', 'function_def_raw.block.funccall.var', _mod('classes', 'print'), 'print(Any) -> None'),
		('Sub.local_ref', 'function_def_raw.block.funccall.arguments.argvalue', _mod('classes', 'bool'), 'bool'),

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

		('Sub.yields', 'function_def_raw.block.yield_stmt', _mod('classes', 'str'), 'str'),

		('Sub.invoke_method', 'function_def_raw.block.funccall.getattr', _mod('__main__', 'Sub.invoke_method'), 'invoke_method(Sub) -> None'),

		('Sub.decl_with_pop', 'function_def_raw.block.assign.assign_namelist.var', _mod('classes', 'int'), 'int'),
		('Sub.decl_with_pop', 'function_def_raw.block.assign.funccall', _mod('classes', 'int'), 'int'),

		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.assign[0].assign_namelist.var', _mod('classes', 'int'), 'int'),
		('Sub.decl_locals.closure', 'function_def_raw.block.assign.assign_namelist.var', _mod('classes', 'list'), 'list<int>'),

		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.for_stmt.for_namelist.name', _mod('classes', 'int'), 'int'),
		('Sub.decl_locals', 'function_def_raw.block.if_stmt[1].if_clause.block.for_stmt.block.try_stmt.except_clauses.except_clause.name', _mod('classes', 'Exception'), 'Exception'),

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

		('Nullable.var_move', 'function_def_raw.block.if_stmt.if_clause.block.return_stmt', _mod('classes', 'str'), 'str'),

		('GenericOps.new', 'function_def_raw.block.assign.funccall', _mod('__main__', 'GenericOps'), 'GenericOps<int>'),
		('GenericOps.cast', 'function_def_raw.block.assign.funccall.arguments.argvalue[0]', _mod('type', 'type'), 'type<GenericOps<Base>>'),

		('WithOps.file_load', 'function_def_raw.block.with_stmt.with_items.with_item', _mod('typing', 'IO'), 'IO'),
		('WithOps.file_load', 'function_def_raw.block.with_stmt.block.assign', _mod('classes', 'dict'), 'dict<str, Any>'),

		('ForRelay.group_receiver.s', '', _mod('classes', 'list'), 'list<str>'),

		('ForFuncCall.cls_call', 'function_def_raw.block.return_stmt.funccall', _mod('classes', 'str'), 'str'),
		('ForFuncCall.self_call', 'function_def_raw.block.return_stmt.funccall', _mod('classes', 'int'), 'int'),
		('ForFuncCall.func_call', 'function_def_raw.block.funccall', _mod('classes', 'bool'), 'bool'),
		('ForFuncCall.relay_call', 'function_def_raw.block.funccall', _mod('__main__', 'ForFuncCall'), 'ForFuncCall'),
		('ForFuncCall.call_to_call', 'function_def_raw.block.funccall', _mod('classes', 'int'), 'int'),
		('ForFuncCall.indexer_call', 'function_def_raw.block.funccall', _mod('classes', 'int'), 'int'),
		('ForFuncCall.callable_call', 'function_def_raw.block.return_stmt.funccall', _mod('__main__', 'T'), 'T'),

		('ForFunction.anno_param', 'function_def_raw.parameters.paramvalue[1].typedparam.name', _mod('classes', 'int'), 'int'),
		('ForFunction.anno_param', 'function_def_raw.parameters.paramvalue[2].typedparam.name', _mod('classes', 'bool'), 'bool'),

		('ForClass.DeclThisVar', '', _mod('type', 'type'), 'type<DeclThisVar>'),
		('ForClass.DeclThisVar.cls_n', '', _mod('classes', 'int'), 'int'),
		('ForClass.DeclThisVar.anno_dsn', '', _mod('classes', 'dict'), 'dict<str, int>'),
		('ForClass.DeclThisVar.n', '', _mod('classes', 'int'), 'int'),
		('ForClass.DeclThisVar.sp', '', _mod('typing', 'Union'), 'Union<str, None>'),
		('ForClass.DeclThisVar.ab', '', _mod('classes', 'bool'), 'bool'),
		('ForClass.DeclThisVar.ac', '', _mod('typing', 'Union'), 'Union<DeclThisVar, None>'),
		('ForClass.DeclThisVar.__init__', 'function_def_raw.block.assign[5]', _mod('classes', 'int'), 'int'),

		('ForEnum.ref_props.es_a_name', '', _mod('classes', 'str'), 'str'),
		('ForEnum.ref_props.es_a_value', '', _mod('classes', 'str'), 'str'),
		('ForEnum.ref_props.en_b_name', '', _mod('classes', 'str'), 'str'),
		('ForEnum.ref_props.en_b_value', '', _mod('classes', 'int'), 'int'),

		('ForTemplateClass.boundary_call', 'function_def_raw.block.return_stmt', _mod('__main__', 'Base'), 'Base'),
		('ForTemplateClass.G3.v_ref.g1', '', _mod('__main__', 'ForTemplateClass.G1'), 'G1<int>'),
		('ForTemplateClass.G3.v_ref.g1_v', '', _mod('classes', 'int'), 'int'),
		('ForTemplateClass.G3.v_ref.g2', '', _mod('__main__', 'ForTemplateClass.G2'), 'G2<int>'),
		('ForTemplateClass.G3.v_ref.g2_v', '', _mod('__main__', 'ForTemplateClass.G1'), 'G1<int>'),
		('ForTemplateClass.G3.v_ref.g3_v', '', _mod('classes', 'int'), 'int'),

		('ForLambda.params.func', '', _mod('collections', 'Callable'), 'Callable<str, int>'),
		('ForLambda.params', 'function_def_raw.block.funccall[1].group_expr.lambdadef', _mod('collections', 'Callable'), 'Callable<int, None>'),
		('ForLambda.params', 'function_def_raw.block.funccall[2].arguments.argvalue.lambdadef', _mod('collections', 'Callable'), 'Callable<bool, int, str>'),
		('ForLambda.params.ret', '', _mod('classes', 'int'), 'int'),

		('ForLambda.expression', 'function_def_raw.block.lambdadef', _mod('collections', 'Callable'), 'Callable<str>'),
		('ForLambda.expression.f', '', _mod('collections', 'Callable'), 'Callable<bool>'),
		('ForLambda.expression.b', '', _mod('classes', 'bool'), 'bool'),
		('ForLambda.expression.ns', '', _mod('classes', 'list'), 'list<int>'),
	])
	def test_type_of(self, local_path: str, offset_path: str, expected: str, attrs_expected: str) -> None:
		reflections = self.fixture.get(Reflections)
		via = reflections.from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path))
		full_path = ModuleDSN.local_joined(via.node.full_path, offset_path)
		node = self.fixture.shared_module.entrypoint.whole_by(full_path)
		symbol = reflections.type_of(node)
		self.assertEqual(symbol.types.fullyname, expected)
		self.assertEqual(symbol.pretty, attrs_expected)

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
