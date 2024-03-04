from unittest import TestCase

from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.implementation import override
import rogw.tranp.syntax.node.definition as defs  # XXX テストを拡充するため実装クラスを使用
from rogw.tranp.syntax.node.node import Node, T_Node
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestNode(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		('...', 'file_input', f'<Entrypoint: {fixture_module_path}>'),
		('class A: ...', 'file_input.class_def', f'<Class: {fixture_module_path}.A>'),
		('def func() -> None: ...', 'file_input.function_def', f'<Function: {fixture_module_path}.func>'),
	])
	def test___str__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(str(node), expected)

	@data_provider([
		('...', 'file_input', '<Entrypoint: file_input>'),
		('class A: ...', 'file_input.class_def', '<Class: file_input.class_def>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: file_input.function_def>'),
	])
	def test___repr__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.__repr__(), expected)

	@data_provider([
		('...', 'file_input', 'file_input', True),
		('class A: ...', 'file_input.class_def', 'file_input.class_def', True),
		('class A: ...', 'file_input', 'file_input.class_def', False),
	])
	def test___eq__(self, source: str, full_path_a: str, full_path_b: str, expected: bool) -> None:
		node_a = self.fixture.custom_nodes(source).by(full_path_a)
		node_b = self.fixture.custom_nodes(source).by(full_path_b)
		self.assertEqual(node_a == node_b, expected)

	@data_provider([
		('...', 'file_input', f'{fixture_module_path}'),
		('class A: ...', 'file_input.class_def', f'{fixture_module_path}'),
		('def func() -> None: ...', 'file_input.function_def', f'{fixture_module_path}'),
	])
	def test_module_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.module_path, expected)

	@data_provider([
		('...', 'file_input', 'file_input'),
		('class A: ...', 'file_input.class_def', 'file_input.class_def'),
		('def func() -> None: ...', 'file_input.function_def', 'file_input.function_def'),
	])
	def test_full_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.full_path, expected)

	@data_provider([
		('...', 'file_input', 'file_input'),
		('class A: ...', 'file_input.class_def', 'class_def'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'block'),
		('class E(CEnum): ...', 'file_input.class_def', 'class_def'),
		('def func() -> None: ...', 'file_input.function_def', 'function_def'),
		('if 1: ...', 'file_input.if_stmt', 'if_stmt'),
		('1', 'file_input.number', 'number'),
		('[a for a in []]', 'file_input.list_comp', 'list_comp'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', 'dict_comp'),
	])
	def test_tag(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.tag, expected)

	@data_provider([
		('...', 'file_input', 'entrypoint'),
		('class A: ...', 'file_input.class_def', 'class'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'block'),
		('class E(CEnum): ...', 'file_input.class_def', 'enum'),
		('def func() -> None: ...', 'file_input.function_def', 'function'),
		('if 1: ...', 'file_input.if_stmt', 'if'),
		('1', 'file_input.number', 'integer'),
		('[a for a in []]', 'file_input.list_comp', 'list_comp'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', 'dict_comp'),
	])
	def test_classification(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.classification, expected)

	@data_provider([
		('...', 'file_input', f'{fixture_module_path}'),
		('class A: ...', 'file_input.class_def', f'{fixture_module_path}.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', f'{fixture_module_path}.A'),
		('class E(CEnum): ...', 'file_input.class_def', f'{fixture_module_path}.E'),
		('def func() -> None: ...', 'file_input.function_def', f'{fixture_module_path}.func'),
		('if True: ...', 'file_input.if_stmt', f'{fixture_module_path}.if'),
		('for i in [0]: ...', 'file_input.for_stmt', f'{fixture_module_path}.for'),
		('while True: ...', 'file_input.while_stmt', f'{fixture_module_path}.while'),
		('1', 'file_input.number', f'{fixture_module_path}'),
		('[a for a in []]', 'file_input.list_comp', f'{fixture_module_path}.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', f'{fixture_module_path}.dict_comp@1'),
	])
	def test_scope(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.scope, expected)

	@data_provider([
		('...', 'file_input', f'{fixture_module_path}'),
		('class A: ...', 'file_input.class_def', f'{fixture_module_path}.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', f'{fixture_module_path}.A'),
		('class E(CEnum): ...', 'file_input.class_def', f'{fixture_module_path}.E'),
		('def func() -> None: ...', 'file_input.function_def', f'{fixture_module_path}.func'),
		('if 1: ...', 'file_input.if_stmt', f'{fixture_module_path}'),
		('1', 'file_input.number', f'{fixture_module_path}'),
		('[a for a in []]', 'file_input.list_comp', f'{fixture_module_path}.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', f'{fixture_module_path}.dict_comp@1'),
	])
	def test_namespace(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.namespace, expected)

	@data_provider([
		('...', 'file_input', ''),
		('class A: ...', 'file_input.class_def.class_def_raw.name', 'A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', ''),
		('class E(CEnum): ...', 'file_input.class_def.class_def_raw.name', 'E'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.name', 'func'),
		('if 1: ...', 'file_input.if_stmt.block', ''),
		('1', 'file_input.number', '1'),
	])
	def test_tokens(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.tokens, expected)

	@data_provider([
		('class A: ...', 'file_input.class_def', 'entrypoint'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'class'),
		('class E(CEnum): ...', 'file_input.class_def', 'entrypoint'),
		('def func() -> None: ...', 'file_input.function_def', 'entrypoint'),
		('if 1: ...', 'file_input.if_stmt', 'entrypoint'),
		('1', 'file_input.number', 'entrypoint'),
	])
	def test_parent(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.parent.classification, expected)

	@data_provider([
		('...', 'file_input', True),
		('class A: ...', 'file_input.class_def', True),
		('class A: ...', 'file_input.class_def.class_def_raw.block', True),
		('class E(CEnum): ...', 'file_input.class_def', True),
		('def func() -> None: ...', 'file_input.function_def', True),
		('if 1: ...', 'file_input.if_stmt', True),
		('1', 'file_input.number', False),
	])
	def test_can_expand(self, source: str, full_path: str, expected: bool) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.can_expand, expected)

	@data_provider([
		# ClassDef
		('def func() -> None: ...', 'file_input.function_def', defs.Function, 'func', f'{fixture_module_path}.func'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.ClassMethod, 'c_method', f'{fixture_module_path}.A.c_method'),
		('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Constructor, '__init__', f'{fixture_module_path}.A.__init__'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Method, 'method', f'{fixture_module_path}.A.method'),
		('class A:\n\tdef method(self) -> None:\n\t\tdef closure() -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.function_def', defs.Closure, 'closure', f'{fixture_module_path}.A.method.closure'),
		('class A: ...', 'file_input.class_def', defs.Class, 'A', f'{fixture_module_path}.A'),
		('class E(CEnum): ...', 'file_input.class_def', defs.Enum, 'E', f'{fixture_module_path}.E'),
		# Declable
		('class A:\n\ta: int = 0', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclClassVar, 'a', f'{fixture_module_path}.A.a'),
		('class A:\n\tdef __init__(self) -> None:\n\t\tself.a: int = 0', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign.assign_namelist.getattr', defs.DeclThisVar, 'a', f'{fixture_module_path}.A.a'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam, 'cls', f'{fixture_module_path}.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam, 'self', f'{fixture_module_path}.A.method.self'),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar, 'i', f'{fixture_module_path}.for.i'),
		('try:\n\ta\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar, 'e', f'{fixture_module_path}.try.e'),
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar, 'a', f'{fixture_module_path}.a'),
		('class A: ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, 'A', f'{fixture_module_path}.A.A'),
		('from a.b.c import A', 'file_input.import_stmt.import_names.name', defs.ImportName, 'A', f'{fixture_module_path}.A'),
		('[a for a in []]', 'file_input.list_comp.comprehension.comp_fors.comp_for.for_namelist.name', defs.DeclLocalVar, 'a', f'{fixture_module_path}.list_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[0]', defs.DeclLocalVar, 'a', f'{fixture_module_path}.dict_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[1]', defs.DeclLocalVar, 'b', f'{fixture_module_path}.dict_comp@1.b'),
		# Reference
		('a.b', 'file_input.getattr', defs.Relay, 'a.b', f'{fixture_module_path}.a.b'),
		('if True:\n\tif True:\n\t\ta.b', 'file_input.if_stmt.block.if_stmt.block.getattr', defs.Relay, 'a.b', f'{fixture_module_path}.if.if.a.b'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None:\n\t\tprint(cls)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ClassRef, 'cls', f'{fixture_module_path}.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None:\n\t\tprint(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ThisRef, 'self', f'{fixture_module_path}.A.method.self'),
		('a', 'file_input.var', defs.Var, 'a', f'{fixture_module_path}.a'),
		('{"a": 1}.items()', 'file_input.funccall.getattr', defs.Relay, 'dict@3.items', f'{fixture_module_path}.dict@3.items'),
		('a[0].items()', 'file_input.funccall.getattr', defs.Relay, 'items', f'{fixture_module_path}.items'),  # XXX Indexerに名前は不要ではあるが一意性が無くて良いのか検討
		# Type
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType, 'int', f'{fixture_module_path}.int'),
		('if True:\n\ta: int = 0', 'file_input.if_stmt.block.anno_assign.typed_var', defs.VarOfType, 'int', f'{fixture_module_path}.if.int'),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType, 'list', f'{fixture_module_path}.list'),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType, 'dict', f'{fixture_module_path}.dict'),
		('a: Callable[[int], None] = {}', 'file_input.anno_assign.typed_getitem', defs.CallableType, 'Callable', f'{fixture_module_path}.Callable'),
		('a: int | str = 0', 'file_input.anno_assign.typed_or_expr', defs.UnionType, 'Union', f'{fixture_module_path}.Union'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.typed_none', defs.NullType, 'None', f'{fixture_module_path}.func.None'),
		# Literal
		('1', 'file_input.number', defs.Integer, 'int@1', f'{fixture_module_path}.int@1'),
		('1.0', 'file_input.number', defs.Float, 'float@1', f'{fixture_module_path}.float@1'),
		("'string'", 'file_input.string', defs.String, 'str@1', f'{fixture_module_path}.str@1'),
		('True', 'file_input.const_true', defs.Truthy, 'bool@1', f'{fixture_module_path}.bool@1'),
		('False', 'file_input.const_false', defs.Falsy, 'bool@1', f'{fixture_module_path}.bool@1'),
		('{1: 2}', 'file_input.dict.key_value', defs.Pair, 'Pair@2', f'{fixture_module_path}.Pair@2'),
		('[1]', 'file_input.list', defs.List, 'list@1', f'{fixture_module_path}.list@1'),
		('{1: 2}', 'file_input.dict', defs.Dict, 'dict@1', f'{fixture_module_path}.dict@1'),
		('None', 'file_input.const_none', defs.Null, 'None', f'{fixture_module_path}.None'),
		# Statement compound
		('if True: ...', 'file_input.if_stmt.block', defs.Block, '', f'{fixture_module_path}.if.block@3'),
		('if True: ...', 'file_input.if_stmt', defs.If, '', f'{fixture_module_path}.if@1'),
		('[a for a in []]', 'file_input.list_comp', defs.ListComp, 'list_comp@1', f'{fixture_module_path}.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', defs.DictComp, 'dict_comp@1', f'{fixture_module_path}.dict_comp@1'),
		# Statement simple
		('a = 0', 'file_input.assign', defs.MoveAssign, '', f'{fixture_module_path}.move_assign@1'),
		('a: int = 0', 'file_input.anno_assign', defs.AnnoAssign, '', f'{fixture_module_path}.anno_assign@1'),
		('a += 1', 'file_input.aug_assign', defs.AugAssign, '', f'{fixture_module_path}.aug_assign@1'),
		# Primary
		('a(0)', 'file_input.funccall', defs.FuncCall, 'func_call@1', f'{fixture_module_path}.func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.funccall', defs.FuncCall, 'func_call@1', f'{fixture_module_path}.func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.for_stmt.for_in.funccall', defs.FuncCall, 'func_call@14', f'{fixture_module_path}.for.func_call@14'),
	])
	def test_i_domain(self, source: str, full_path: str, types: type[T_Node], expected_name: bool, expected_fully: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(type(node), types)
		self.assertEqual(node.domain_name, expected_name)
		self.assertEqual(node.fullyname, expected_fully)

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_var',
			'file_input.class_def.class_def_raw.block.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].number',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[2]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
		]),
	])
	def test_procedural_flow(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes.by(full_path)
		all = [in_node.full_path for in_node in node.procedural()]
		try:
			self.assertEqual(all, expected)
		except AssertionError:
			import json
			print(json.dumps(all, indent=2))
			raise

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_var',
			'file_input.class_def.class_def_raw.block.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1]',
			'file_input.class_def.class_def_raw.block.class_def',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[2]',
		]),
	])
	def test_procedural_ast(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes.by(full_path)
		all = [in_node.full_path for in_node in node.procedural(order='ast')]
		try:
			self.assertEqual(all, expected)
		except AssertionError:
			import json
			print(json.dumps(all, indent=2))
			raise

	def test_is_a(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(node.is_a(defs.Function), True)
		self.assertEqual(node.is_a(defs.ClassMethod), False)
		self.assertEqual(node.is_a(defs.Method), True)
		self.assertEqual(node.is_a(defs.Class), False)
		self.assertEqual(node.is_a(defs.ClassDef), True)

	def test_as_a(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(type(node), defs.Method)
		self.assertEqual(type(node.as_a(defs.Function)), defs.Method)
		self.assertEqual(type(node.as_a(defs.ClassDef)), defs.Method)

	def test_one_of(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__')
		self.assertEqual(type(node), defs.Empty)
		self.assertEqual(type(node.one_of(defs.Type | defs.Empty)), defs.Empty)

	def test_match_feature(self) -> None:
		class NodeA(Node):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tag == 'node_a'

		invoker = self.fixture.get(Invoker)
		node_a = invoker(NodeA, 'node_a')
		node_b = invoker(NodeA, 'node_b')
		self.assertEqual(NodeA.match_feature(node_a), True)
		self.assertEqual(NodeA.match_feature(node_b), False)

	def test_dirty_proxify(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number')
		proxy = node.dirty_proxify(tokens='10')
		self.assertEqual(isinstance(node, defs.Number), True)
		self.assertEqual(isinstance(proxy, defs.Number), True)
		self.assertEqual(node.tokens, '1')
		self.assertEqual(proxy.tokens, '10')

	@data_provider([
		("""
class A:
	def __init__(self, n: int) -> None:
		self.n: dict[str, int] = {'key': n}
		if True:
			n = 1
			a.b(c, d)
		for key, value in {'a': 1}.items():
			...
""",
			'file_input',
			[
				'<Entrypoint: tests.unit.rogw.tranp.syntax.node.fixtures.test_node>',
				'+-statements:',
				'  +-<Class: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A>',
				'    +-symbol: <TypesName: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.A>',
				'    +-decorators:',
				'    +-inherits:',
				'    +-generic_types:',
				'    +-comment: <Proxy: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.Empty>',
				'    +-statements:',
				'      +-<Constructor: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__>',
				'        +-symbol: <TypesName: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.__init__>',
				'        +-decorators:',
				'        +-parameters:',
				'        | +-<Parameter: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.parameter@14>',
				'        | | +-symbol: <DeclThisParam: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.self>',
				'        | | +-var_type: <Empty: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.Empty>',
				'        | | +-default_value: <Empty: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.Empty>',
				'        | +-<Parameter: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.parameter@20>',
				'        |   +-symbol: <DeclParam: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.n>',
				'        |   +-var_type: <VarOfType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.int>',
				'        |   +-default_value: <Empty: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.Empty>',
				'        +-return_type: <NullType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.None>',
				'        +-comment: <Proxy: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.Empty>',
				'        +-statements:',
				'          +-<AnnoAssign: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.anno_assign@31>',
				'          | +-receiver: <DeclThisVar: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.n>',
				'          | +-var_type: <DictType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.dict>',
				'          | | +-type_name: <VarOfType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.dict>',
				'          | | +-key_type: <VarOfType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.str>',
				'          | | +-value_type: <VarOfType: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.int>',
				'          | +-value: <Dict: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.dict@50>',
				'          |   +-items:',
				'          |     +-<Pair: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.Pair@51>',
				'          |       +-first: <String: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.str@52>',
				'          |       +-second: <Var: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.n>',
				'          +-<If: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if@57>',
				'          | +-condition: <Truthy: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.bool@58>',
				'          | +-statements:',
				'          | | +-<MoveAssign: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.move_assign@60>',
				'          | | | +-receivers:',
				'          | | | | +-<DeclLocalVar: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.n>',
				'          | | | +-value: <Integer: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.int@65>',
				'          | | +-<FuncCall: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.func_call@67>',
				'          | |   +-calls: <Relay: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.a.b>',
				'          | |   | +-receiver: <Var: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.a>',
				'          | |   +-arguments:',
				'          | |     +-<Argument: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.argument@75>',
				'          | |     | +-label: <Proxy: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.Empty>',
				'          | |     | +-value: <Var: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.c>',
				'          | |     +-<Argument: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.argument@79>',
				'          | |       +-label: <Proxy: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.Empty>',
				'          | |       +-value: <Var: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.if.d>',
				'          | +-else_ifs:',
				'          | +-else_statements:',
				'          +-<For: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for@85>',
				'            +-symbols:',
				'            | +-<DeclLocalVar: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.key>',
				'            | +-<DeclLocalVar: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.value>',
				'            +-for_in: <ForIn: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.for_in@91>',
				'            | +-iterates: <FuncCall: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.func_call@92>',
				'            |   +-calls: <Relay: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.dict@94.items>',
				'            |   | +-receiver: <Dict: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.dict@94>',
				'            |   |   +-items:',
				'            |   |     +-<Pair: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.Pair@95>',
				'            |   |       +-first: <String: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.str@96>',
				'            |   |       +-second: <Integer: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.int@98>',
				'            |   +-arguments:',
				'            +-statements:',
				'              +-<Elipsis: tests.unit.rogw.tranp.syntax.node.fixtures.test_node.A.__init__.for.elipsis@104>',
			],
	),])
	def test_pretty(self, source: str, full_path: str, expected: list[str]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)

		try:
			self.assertEqual(node.pretty().split('\n'), expected)
		except AssertionError:
			print(node.pretty())
