from typing import Callable, cast
from unittest import TestCase

from py2cpp.lang.locator import Currying
from py2cpp.lang.implementation import override
from py2cpp.node.embed import Meta, actualized
from py2cpp.node.interface import ITerminal
import py2cpp.node.definition as defs  # XXX テストを拡充するため実装クラスを使用
from py2cpp.node.node import Node
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestNode(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('...', 'file_input', '<Entrypoint: file_input>'),
		('class A: ...', 'file_input.class_def', '<Class: file_input.class_def>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: file_input.function_def>'),
	])
	def test___str__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(str(node), expected)

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
		('...', 'file_input', ''),
		('class A: ...', 'file_input.class_def', 'A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', ''),
		('class E(CEnum): ...', 'file_input.enum_def', 'E'),
		('def func() -> None: ...', 'file_input.function_def', 'func'),
		('if 1: ...', 'file_input.if_stmt', ''),
		('1', 'file_input.number', ''),
	])
	def test_public_name(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		self.assertEqual(node.public_name, expected)

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
		self.assertEqual((not isinstance(node, ITerminal)) or cast(ITerminal, node).can_expand, expected)

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
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block',
			'file_input.class_def.class_def_raw.block.enum_def',
			'file_input.class_def.class_def_raw.block.enum_def.name',
			'file_input.class_def.class_def_raw.block.enum_def.block',
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
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block',
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
			'file_input.class_def.class_def_raw.block.enum_def.block',
			'file_input.class_def.class_def_raw.block.enum_def',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.return_type',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].block',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].block',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.return_type',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block',
			'file_input.class_def.class_def_raw.block.function_def[2]',
			'file_input.class_def.class_def_raw.block',
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
