from unittest import TestCase

from rogw.tranp.lang.implementation import override
import rogw.tranp.syntax.node.definition as defs  # XXX テストを拡充するため実装クラスを使用
from rogw.tranp.syntax.node.node import Node, T_Node
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestNode(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		('...', 'file_input', '<Entrypoint: __main__ (1, 1)..(2, 1)>'),
		('class A: ...', 'file_input.class_def', '<Class: __main__.A (1, 1)..(2, 1)>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: __main__.func (1, 1)..(2, 1)>'),
	])
	def test___str__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(str(node), expected)

	@data_provider([
		('...', 'file_input', '<Entrypoint: file_input>'),
		('class A: ...', 'file_input.class_def', '<Class: file_input.class_def>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: file_input.function_def>'),
	])
	def test___repr__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.__repr__(), expected)

	@data_provider([
		('...', 'file_input', 'file_input', True),
		('class A: ...', 'file_input.class_def', 'file_input.class_def', True),
		('class A: ...', 'file_input', 'file_input.class_def', False),
	])
	def test___eq__(self, source: str, full_path_a: str, full_path_b: str, expected: bool) -> None:
		node_a = self.fixture.custom_nodes_by(source, full_path_a)
		node_b = self.fixture.custom_nodes_by(source, full_path_b)
		self.assertEqual(node_a == node_b, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__'),
		('def func() -> None: ...', 'file_input.function_def', '__main__'),
	])
	def test_module_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.module_path, expected)

	@data_provider([
		('...', 'file_input', 'file_input'),
		('class A: ...', 'file_input.class_def', 'file_input.class_def'),
		('def func() -> None: ...', 'file_input.function_def', 'file_input.function_def'),
	])
	def test_full_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.classification, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', '__main__.A'),
		('class E(CEnum): ...', 'file_input.class_def', '__main__.E'),
		('def func() -> None: ...', 'file_input.function_def', '__main__.func'),
		('if True: ...', 'file_input.if_stmt', '__main__.if'),
		('for i in [0]: ...', 'file_input.for_stmt', '__main__.for'),
		('while True: ...', 'file_input.while_stmt', '__main__.while'),
		('1', 'file_input.number', '__main__'),
		('[a for a in []]', 'file_input.list_comp', '__main__.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', '__main__.dict_comp@1'),
	])
	def test_scope(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.scope, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', '__main__.A'),
		('class E(CEnum): ...', 'file_input.class_def', '__main__.E'),
		('def func() -> None: ...', 'file_input.function_def', '__main__.func'),
		('if 1: ...', 'file_input.if_stmt', '__main__'),
		('1', 'file_input.number', '__main__'),
		('[a for a in []]', 'file_input.list_comp', '__main__.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', '__main__.dict_comp@1'),
	])
	def test_namespace(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.can_expand, expected)

	@data_provider([
		# ClassDef
		('def func() -> None: ...', 'file_input.function_def', defs.Function, 'func', '__main__.func'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.ClassMethod, 'c_method', '__main__.A.c_method'),
		('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Constructor, '__init__', '__main__.A.__init__'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Method, 'method', '__main__.A.method'),
		('class A:\n\tdef method(self) -> None:\n\t\tdef closure() -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.function_def', defs.Closure, 'closure', '__main__.A.method.closure'),
		('class A: ...', 'file_input.class_def', defs.Class, 'A', '__main__.A'),
		('class E(CEnum): ...', 'file_input.class_def', defs.Enum, 'E', '__main__.E'),
		# Declable
		('class A:\n\ta: int = 0', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclClassVar, 'a', '__main__.A.a'),
		('class A:\n\tdef __init__(self) -> None:\n\t\tself.a: int = 0', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign.assign_namelist.getattr', defs.DeclThisVar, 'a', '__main__.A.a'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam, 'cls', '__main__.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam, 'self', '__main__.A.method.self'),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar, 'i', '__main__.for.i'),
		('try:\n\ta\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar, 'e', '__main__.try.e'),
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar, 'a', '__main__.a'),
		('class A: ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, 'A', '__main__.A.A'),
		('from a.b.c import A', 'file_input.import_stmt.import_names.name', defs.ImportName, 'A', '__main__.A'),
		('[a for a in []]', 'file_input.list_comp.comprehension.comp_fors.comp_for.for_namelist.name', defs.DeclLocalVar, 'a', '__main__.list_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[0]', defs.DeclLocalVar, 'a', '__main__.dict_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[1]', defs.DeclLocalVar, 'b', '__main__.dict_comp@1.b'),
		# Reference
		('a.b', 'file_input.getattr', defs.Relay, 'a.b', '__main__.a.b'),
		('if True:\n\tif True:\n\t\ta.b', 'file_input.if_stmt.block.if_stmt.block.getattr', defs.Relay, 'a.b', '__main__.if.if.a.b'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None:\n\t\tprint(cls)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ClassRef, 'cls', '__main__.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None:\n\t\tprint(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ThisRef, 'self', '__main__.A.method.self'),
		('a', 'file_input.var', defs.Var, 'a', '__main__.a'),
		('{"a": 1}.items()', 'file_input.funccall.getattr', defs.Relay, 'dict@3.items', '__main__.dict@3.items'),
		('a[0].items()', 'file_input.funccall.getattr', defs.Relay, 'items', '__main__.items'),  # XXX Indexerに名前は不要ではあるが一意性が無くて良いのか検討
		# Type
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType, 'int', '__main__.int'),
		('if True:\n\ta: int = 0', 'file_input.if_stmt.block.anno_assign.typed_var', defs.VarOfType, 'int', '__main__.if.int'),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType, 'list', '__main__.list'),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType, 'dict', '__main__.dict'),
		('a: Callable[[int], None] = {}', 'file_input.anno_assign.typed_getitem', defs.CallableType, 'Callable', '__main__.Callable'),
		('a: int | str = 0', 'file_input.anno_assign.typed_or_expr', defs.UnionType, 'Union', '__main__.Union'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.typed_none', defs.NullType, 'None', '__main__.func.None'),
		# Literal
		('1', 'file_input.number', defs.Integer, 'int@1', '__main__.int@1'),
		('1.0', 'file_input.number', defs.Float, 'float@1', '__main__.float@1'),
		("'string'", 'file_input.string', defs.String, 'str@1', '__main__.str@1'),
		('True', 'file_input.const_true', defs.Truthy, 'bool@1', '__main__.bool@1'),
		('False', 'file_input.const_false', defs.Falsy, 'bool@1', '__main__.bool@1'),
		('{1: 2}', 'file_input.dict.key_value', defs.Pair, 'Pair@2', '__main__.Pair@2'),
		('[1]', 'file_input.list', defs.List, 'list@1', '__main__.list@1'),
		('{1: 2}', 'file_input.dict', defs.Dict, 'dict@1', '__main__.dict@1'),
		('None', 'file_input.const_none', defs.Null, 'None', '__main__.None'),
		# Statement compound
		('if True: ...', 'file_input.if_stmt.block', defs.Block, '', '__main__.if.block@3'),
		('if True: ...', 'file_input.if_stmt', defs.If, '', '__main__.if@1'),
		('[a for a in []]', 'file_input.list_comp', defs.ListComp, 'list_comp@1', '__main__.list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', defs.DictComp, 'dict_comp@1', '__main__.dict_comp@1'),
		# Statement simple
		('a = 0', 'file_input.assign', defs.MoveAssign, '', '__main__.move_assign@1'),
		('a: int = 0', 'file_input.anno_assign', defs.AnnoAssign, '', '__main__.anno_assign@1'),
		('a += 1', 'file_input.aug_assign', defs.AugAssign, '', '__main__.aug_assign@1'),
		# Primary
		('a(0)', 'file_input.funccall', defs.FuncCall, 'func_call@1', '__main__.func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.funccall', defs.FuncCall, 'func_call@1', '__main__.func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.for_stmt.for_in.funccall', defs.FuncCall, 'func_call@14', '__main__.for.func_call@14'),
	])
	def test_i_domain(self, source: str, full_path: str, types: type[T_Node], expected_name: bool, expected_fully: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
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
		node = self.fixture.shared_nodes_by(full_path)
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
		node = self.fixture.shared_nodes_by(full_path)
		all = [in_node.full_path for in_node in node.procedural(order='ast')]
		try:
			self.assertEqual(all, expected)
		except AssertionError:
			import json
			print(json.dumps(all, indent=2))
			raise

	def test_is_a(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(node.is_a(defs.Function), True)
		self.assertEqual(node.is_a(defs.ClassMethod), False)
		self.assertEqual(node.is_a(defs.Method), True)
		self.assertEqual(node.is_a(defs.Class), False)
		self.assertEqual(node.is_a(defs.ClassDef), True)

	def test_as_a(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(type(node), defs.Method)
		self.assertEqual(type(node.as_a(defs.Function)), defs.Method)
		self.assertEqual(type(node.as_a(defs.ClassDef)), defs.Method)

	def test_one_of(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__')
		self.assertEqual(type(node), defs.Empty)
		self.assertEqual(type(node.one_of(defs.Type | defs.Empty)), defs.Empty)

	def test_match_feature(self) -> None:
		class NodeA(Node):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tokens == 'a'

		entrypoint = self.fixture.custom_nodes_by('a\nb', 'file_input').as_a(defs.Entrypoint)
		node_a = entrypoint.whole_by('file_input.var[0]')
		node_b = entrypoint.whole_by('file_input.var[1]')
		self.assertEqual(NodeA.match_feature(node_a), True)
		self.assertEqual(NodeA.match_feature(node_b), False)

	def test_dirty_proxify(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number')
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
				'<Entrypoint: __main__ (1, 1)..(11, 1)>',
				'+-statements:',
				'  +-<Class: __main__.A (2, 1)..(11, 1)>',
				'    +-symbol: <TypesName: __main__.A.A (2, 7)..(2, 8)>',
				'    +-decorators:',
				'    +-inherits:',
				'    +-generic_types:',
				'    +-comment: <Proxy: __main__.A.Empty (0, 0)..(0, 0)>',
				'    +-statements:',
				'      +-<Constructor: __main__.A.__init__ (3, 2)..(11, 1)>',
				'        +-symbol: <TypesName: __main__.A.__init__.__init__ (3, 6)..(3, 14)>',
				'        +-decorators:',
				'        +-parameters:',
				'        | +-<Parameter: __main__.A.__init__.parameter@14 (3, 15)..(3, 19)>',
				'        | | +-symbol: <DeclThisParam: __main__.A.__init__.self (3, 15)..(3, 19)>',
				'        | | +-var_type: <Empty: __main__.A.__init__.Empty (0, 0)..(0, 0)>',
				'        | | +-default_value: <Empty: __main__.A.__init__.Empty (0, 0)..(0, 0)>',
				'        | +-<Parameter: __main__.A.__init__.parameter@20 (3, 21)..(3, 27)>',
				'        |   +-symbol: <DeclParam: __main__.A.__init__.n (3, 21)..(3, 22)>',
				'        |   +-var_type: <VarOfType: __main__.A.__init__.int (3, 24)..(3, 27)>',
				'        |   +-default_value: <Empty: __main__.A.__init__.Empty (0, 0)..(0, 0)>',
				'        +-return_type: <NullType: __main__.A.__init__.None (3, 32)..(3, 36)>',
				'        +-comment: <Proxy: __main__.A.__init__.Empty (0, 0)..(0, 0)>',
				'        +-statements:',
				'          +-<AnnoAssign: __main__.A.__init__.anno_assign@31 (4, 3)..(4, 38)>',
				'          | +-receiver: <DeclThisVar: __main__.A.n (4, 3)..(4, 9)>',
				'          | +-var_type: <DictType: __main__.A.__init__.dict (4, 11)..(4, 25)>',
				'          | | +-type_name: <VarOfType: __main__.A.__init__.dict (4, 11)..(4, 15)>',
				'          | | +-key_type: <VarOfType: __main__.A.__init__.str (4, 16)..(4, 19)>',
				'          | | +-value_type: <VarOfType: __main__.A.__init__.int (4, 21)..(4, 24)>',
				'          | +-value: <Dict: __main__.A.__init__.dict@50 (4, 28)..(4, 38)>',
				'          |   +-items:',
				'          |     +-<Pair: __main__.A.__init__.Pair@51 (4, 29)..(4, 37)>',
				'          |       +-first: <String: __main__.A.__init__.str@52 (4, 29)..(4, 34)>',
				'          |       +-second: <Var: __main__.A.__init__.n (4, 36)..(4, 37)>',
				'          +-<If: __main__.A.__init__.if@57 (5, 3)..(8, 3)>',
				'          | +-condition: <Truthy: __main__.A.__init__.if.bool@58 (5, 6)..(5, 10)>',
				'          | +-statements:',
				'          | | +-<MoveAssign: __main__.A.__init__.if.move_assign@60 (6, 4)..(6, 9)>',
				'          | | | +-receivers:',
				'          | | | | +-<DeclLocalVar: __main__.A.__init__.if.n (6, 4)..(6, 5)>',
				'          | | | +-value: <Integer: __main__.A.__init__.if.int@65 (6, 8)..(6, 9)>',
				'          | | +-<FuncCall: __main__.A.__init__.if.func_call@67 (7, 4)..(7, 13)>',
				'          | |   +-calls: <Relay: __main__.A.__init__.if.a.b (7, 4)..(7, 7)>',
				'          | |   | +-receiver: <Var: __main__.A.__init__.if.a (7, 4)..(7, 5)>',
				'          | |   +-arguments:',
				'          | |     +-<Argument: __main__.A.__init__.if.argument@75 (7, 8)..(7, 9)>',
				'          | |     | +-label: <Proxy: __main__.A.__init__.if.Empty (0, 0)..(0, 0)>',
				'          | |     | +-value: <Var: __main__.A.__init__.if.c (7, 8)..(7, 9)>',
				'          | |     +-<Argument: __main__.A.__init__.if.argument@79 (7, 11)..(7, 12)>',
				'          | |       +-label: <Proxy: __main__.A.__init__.if.Empty (0, 0)..(0, 0)>',
				'          | |       +-value: <Var: __main__.A.__init__.if.d (7, 11)..(7, 12)>',
				'          | +-else_ifs:',
				'          | +-else_statements:',
				'          +-<For: __main__.A.__init__.for@85 (8, 3)..(11, 1)>',
				'            +-symbols:',
				'            | +-<DeclLocalVar: __main__.A.__init__.for.key (8, 7)..(8, 10)>',
				'            | +-<DeclLocalVar: __main__.A.__init__.for.value (8, 12)..(8, 17)>',
				'            +-for_in: <ForIn: __main__.A.__init__.for.for_in@91 (8, 18)..(8, 37)>',
				'            | +-iterates: <FuncCall: __main__.A.__init__.for.func_call@92 (8, 21)..(8, 37)>',
				'            |   +-calls: <Relay: __main__.A.__init__.for.dict@94.items (8, 21)..(8, 35)>',
				'            |   | +-receiver: <Dict: __main__.A.__init__.for.dict@94 (8, 21)..(8, 29)>',
				'            |   |   +-items:',
				'            |   |     +-<Pair: __main__.A.__init__.for.Pair@95 (8, 22)..(8, 28)>',
				'            |   |       +-first: <String: __main__.A.__init__.for.str@96 (8, 22)..(8, 25)>',
				'            |   |       +-second: <Integer: __main__.A.__init__.for.int@98 (8, 27)..(8, 28)>',
				'            |   +-arguments:',
				'            +-statements:',
				'              +-<Elipsis: __main__.A.__init__.for.elipsis@104 (9, 4)..(9, 7)>',
			],
	),])
	def test_pretty(self, source: str, full_path: str, expected: list[str]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)

		try:
			self.assertEqual(node.pretty().split('\n'), expected)
		except AssertionError:
			print(node.pretty())
