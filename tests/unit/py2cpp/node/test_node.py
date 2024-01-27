from typing import Callable
from unittest import TestCase

from py2cpp.lang.locator import Currying
from py2cpp.lang.implementation import override
import py2cpp.node.definition as defs  # XXX テストを拡充するため実装クラスを使用
from py2cpp.node.embed import Meta, actualized
from py2cpp.node.node import Node, T_Node
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestNode(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('...', 'file_input', '<Entrypoint: __main__.file_input>'),  # FIXME file_inputを削除
		('class A: ...', 'file_input.class_def', '<Class: __main__.A>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: __main__.func>'),
	])
	def test___str__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(str(node), expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__'),
		('def func() -> None: ...', 'file_input.function_def', '__main__'),
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
		('class E(CEnum): ...', 'file_input.enum_def', 'enum_def'),
		('def func() -> None: ...', 'file_input.function_def', 'function_def'),
		('if 1: ...', 'file_input.if_stmt', 'if_stmt'),
		('1', 'file_input.number', 'number'),
	])
	def test_tag(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.tag, expected)

	@data_provider([
		('...', 'file_input', 'entrypoint'),
		('class A: ...', 'file_input.class_def', 'class'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'block'),
		('class E(CEnum): ...', 'file_input.enum_def', 'enum'),
		('def func() -> None: ...', 'file_input.function_def', 'function'),
		('if 1: ...', 'file_input.if_stmt', 'if'),
		('1', 'file_input.number', 'integer'),
	])
	def test_classification(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.classification, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', '__main__.A'),
		('class E(CEnum): ...', 'file_input.enum_def', '__main__.E'),
		('def func() -> None: ...', 'file_input.function_def', '__main__.func'),
		('if 1: ...', 'file_input.if_stmt', '__main__'),
		('1', 'file_input.number', '__main__'),
	])
	def test_scope(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.scope, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__.A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', '__main__.A'),
		('class E(CEnum): ...', 'file_input.enum_def', '__main__.E'),
		('def func() -> None: ...', 'file_input.function_def', '__main__'),
		('if 1: ...', 'file_input.if_stmt', '__main__'),
		('1', 'file_input.number', '__main__'),
	])
	def test_namespace(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.namespace, expected)

	@data_provider([
		('...', 'file_input', ''),
		('class A: ...', 'file_input.class_def.class_def_raw.name', 'A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', ''),
		('class E(CEnum): ...', 'file_input.enum_def.name', 'E'),
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
		('class E(CEnum): ...', 'file_input.enum_def', 'entrypoint'),
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
		('class E(CEnum): ...', 'file_input.enum_def', True),
		('def func() -> None: ...', 'file_input.function_def', True),
		('if 1: ...', 'file_input.if_stmt', True),
		('1', 'file_input.number', False),
	])
	def test_can_expand(self, source: str, full_path: str, expected: bool) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.can_expand, expected)

	@data_provider([
		# ClassKind
		('def func() -> None: ...', 'file_input.function_def', defs.Function, 'func', '__main__.func'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.ClassMethod, 'c_method', '__main__.A.c_method'),
		('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Constructor, '__init__', '__main__.A.__init__'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Method, 'method', '__main__.A.method'),
		('class A:\n\tdef method(self) -> None:\n\t\tdef closure() -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.function_def', defs.Closure, 'closure', '__main__.A.method.closure'),
		('class A: ...', 'file_input.class_def', defs.Class, 'A', '__main__.A'),
		('class E(CEnum): ...', 'file_input.enum_def', defs.Enum, 'E', '__main__.E'),
		# Declable
		('class A:\n\ta: int = 0', 'file_input.class_def.class_def_raw.block.assign_stmt.anno_assign.var', defs.DeclClassVar, 'a', '__main__.A.a'),
		('class A:\n\tdef __init__(self) -> None:\n\t\tself.a: int = 0', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.assign_stmt.anno_assign.getattr', defs.DeclThisVar, 'a', '__main__.A.a'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam, 'cls', '__main__.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam, 'self', '__main__.A.method.self'),
		('for i in range(1): ...', 'file_input.for_stmt.name', defs.DeclLocalVar, 'i', '__main__.i'),
		('try:\n\ta\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar, 'e', '__main__.e'),
		('a = 0', 'file_input.assign_stmt.assign.var', defs.DeclLocalVar, 'a', '__main__.a'),
		('class A: ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, 'A', '__main__.A.A'),
		('from a.b.c import A', 'file_input.import_stmt.import_names.name', defs.ImportName, 'A', '__main__.A'),
		# Reference
		('a.b', 'file_input.getattr', defs.Relay, 'a.b', '__main__.a.b'),
		('if True:\n\tif True:\n\t\ta.b', 'file_input.if_stmt.block.if_stmt.block.getattr', defs.Relay, 'a.b', '__main__.if_stmt.if_stmt.a.b'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None:\n\t\tprint(cls)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ClassRef, 'cls', '__main__.A.c_method.cls'),
		('class A:\n\tdef method(self) -> None:\n\t\tprint(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ThisRef, 'self', '__main__.A.method.self'),
		('a', 'file_input.var', defs.Variable, 'a', '__main__.a'),
		# Type
		('a: int = 0', 'file_input.assign_stmt.anno_assign.typed_var', defs.GeneralType, 'int', '__main__.int'),
		('if True:\n\ta: int = 0', 'file_input.if_stmt.block.assign_stmt.anno_assign.typed_var', defs.GeneralType, 'int', '__main__.if_stmt.int'),
		('a: list[int] = []', 'file_input.assign_stmt.anno_assign.typed_getitem', defs.ListType, 'list', '__main__.list'),
		('a: dict[str, int] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem', defs.DictType, 'dict', '__main__.dict'),
		('a: Callable[[int], None] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem', defs.CallableType, 'Callable', '__main__.Callable'),
		('a: int | str = 0', 'file_input.assign_stmt.anno_assign.typed_or_expr', defs.UnionType, 'Union', '__main__.Union'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.return_type.typed_none', defs.NullType, 'None', '__main__.func.None'),
		# Literal
		('1', 'file_input.number', defs.Integer, 'int', '__main__.int'),
		('1.0', 'file_input.number', defs.Float, 'float', '__main__.float'),
		("'string'", 'file_input.string', defs.String, 'str', '__main__.str'),
		('True', 'file_input.const_true', defs.Truthy, 'bool', '__main__.bool'),
		('False', 'file_input.const_false', defs.Falsy, 'bool', '__main__.bool'),
		('{1: 2}', 'file_input.dict.key_value', defs.Pair, 'pair_', '__main__.pair_'),
		('[1]', 'file_input.list', defs.List, 'list', '__main__.list'),
		('{1: 2}', 'file_input.dict', defs.Dict, 'dict', '__main__.dict'),
		('None', 'file_input.const_none', defs.Null, 'None', '__main__.None'),
	])
	def test_i_domain(self, source: str, full_path: str, types: type[T_Node], expected_name: bool, expected_fully: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(type(node), types)
		self.assertEqual(node.domain_name, expected_name)
		self.assertEqual(node.fullyname, expected_fully)

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.enum_def',
			'file_input.class_def.class_def_raw.block.enum_def.name',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0]',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0].assign.var',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0].assign.number',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1]',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1].assign.var',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1].assign.number',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type.typed_none',
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
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
		]),
	])
	def test_flatten(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes.by(full_path)
		all = [in_node.full_path for in_node in node.flatten()]
		self.assertEqual(all, expected)

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.enum_def.name',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0].assign.var',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0].assign.number',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0]',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1].assign.var',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1].assign.number',
			'file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[1]',
			'file_input.class_def.class_def_raw.block.enum_def',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type.typed_none',
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
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[2]',
		]),
	])
	def test_calculated(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes.by(full_path)
		all = [in_node.full_path for in_node in node.calculated()]
		self.assertEqual(all, expected)

	def test_is_a(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(node.is_a(defs.Function), True)
		self.assertEqual(node.is_a(defs.ClassMethod), False)
		self.assertEqual(node.is_a(defs.Method), True)
		self.assertEqual(node.is_a(defs.Class), False)
		self.assertEqual(node.is_a(defs.ClassKind), True)

	def test_as_a(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(type(node), defs.Method)
		self.assertEqual(type(node.as_a(defs.Function)), defs.Method)
		self.assertEqual(type(node.as_a(defs.ClassKind)), defs.Method)

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

		currying = self.fixture.get(Currying)
		node_a = currying(NodeA, Callable[[str], Node])('node_a')
		node_b = currying(NodeA, Callable[[str], Node])('node_b')
		self.assertEqual(NodeA.match_feature(node_a), True)
		self.assertEqual(NodeA.match_feature(node_b), False)

	def test_actualize(self) -> None:
		class NodeA(Node): pass

		@Meta.embed(Node, actualized(via=NodeA))
		class NodeB(NodeA):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tag == 'node_b'

		currying = self.fixture.get(Currying)
		node = currying(NodeA, Callable[[str], Node])('node_b')
		self.assertEqual(type(node), NodeA)
		self.assertEqual(type(node.actualize()), NodeB)

	def test_dirty_proxify(self) -> None:
		node = self.fixture.shared_nodes.by('file_input.class_def.class_def_raw.block.enum_def.block.assign_stmt[0].assign.number')
		proxy = node.dirty_proxify(tokens='10')
		self.assertEqual(isinstance(node, defs.Number), True)
		self.assertEqual(isinstance(proxy, defs.Number), True)
		self.assertEqual(node.tokens, '1')
		self.assertEqual(proxy.tokens, '10')

	@data_provider([
		('class A:\n\tdef __init__(self, n: int) -> None:\n\t\tself.n: int = n',
			'file_input',
			'\n'.join([
				'<Entrypoint: __main__.file_input>',
				'  statements:',
				'    <Class: __main__.A>',
				'      symbol: <TypesName: __main__.A.A>',
				'      decorators:',
				'      parents:',
				'      statements:',
				'        <Constructor: __main__.A.__init__>',
				'          symbol: <TypesName: __main__.A.__init__.__init__>',
				'          decorators:',
				'          parameters:',
				'            <Parameter: __main__.A.__init__.paramvalue[0]>',
				'              symbol: <DeclThisParam: __main__.A.__init__.self>',
				'              var_type: <Empty: __main__.A.__init__.__empty__>',
				'              default_value: <Empty: __main__.A.__init__.__empty__>',
				'            <Parameter: __main__.A.__init__.paramvalue[1]>',
				'              symbol: <DeclLocalVar: __main__.A.__init__.n>',
				'              var_type: <GeneralType: __main__.A.__init__.int>',
				'              default_value: <Empty: __main__.A.__init__.__empty__>',
				'          return_type: <NullType: __main__.A.__init__.None>',
				'          statements:',
				'            <AnnoAssign: __main__.A.__init__.assign_stmt>',
				'              receiver: <DeclThisVar: __main__.A.n>',
				'              var_type: <GeneralType: __main__.A.__init__.int>',
				'              value: <DeclLocalVar: __main__.A.__init__.n>',
			]),
	),])
	def test_pretty(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.pretty(), expected)
