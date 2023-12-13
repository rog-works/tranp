from typing import TypedDict
from unittest import TestCase

from lark import Token, Tree

from py2cpp.lang.annotation import override
from py2cpp.node.embed import expansionable, Meta
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.provider import Settings
from py2cpp.node.trait import ScopeTrait
from tests.test.helper import data_provider

T_Settings = TypedDict('T_Settings', {'nodes': dict[str, type[Node]], 'fallback': type[Node]})


class Terminal(Node): pass
class Empty(Node): pass
class Assign(Node): pass
class Block(Node, ScopeTrait): pass


class If(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class FileInput(Node):
	@property
	@override
	def scope_name(self) -> str:
		return '__main__'


	@property
	@override
	def namespace(self) -> str:
		return '__main__'


	@property
	@override
	def scope(self) -> str:
		return '__main__'


class Class(Node):
	@property
	@override
	def scope_name(self) -> str:
		return 'Class'


	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class Enum(Node):
	@property
	@override
	def scope_name(self) -> str:
		return 'Enum'


	@property
	@Meta.embed(Node, expansionable(order=0))
	def variables(self) -> list[Assign]:
		return [node.as_a(Assign) for node in self._children('block')]


class Function(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class Fixture:
	@classmethod
	def tree(cls) -> Tree:
		return Tree('file_input', [
			Tree('class', [
				None,
				Tree('block', [
					Tree('enum', [
						Tree('block', [
							Tree('assign', [Token('term_a', '')]),
							Tree('assign', [Token('term_a', '')]),
						]),
					]),
					Tree('function', [
						Tree('block', [
							Tree('if', [
								Tree('block', [
									Token('term_a', ''),
								]),
							]),
						]),
					]),
					Tree('function', [
						Tree('block', [
							Token('term_a', ''),
						]),
					]),
				]),
			]),
			Tree('function', [
				Tree('block', [
					Token('term_a', ''),
				]),
			]),
		])


	@classmethod
	def resolver(cls) -> NodeResolver:
		return NodeResolver.load(Settings(
			symbols={
				'file_input': FileInput,
				'class': Class,
				'enum': Enum,
				'function': Function,
				'if': If,
				'assign': Assign,
				'block': Block,
				'__empty__': Empty,
			},
			fallback=Terminal
		))


	@classmethod
	def nodes(cls) -> Nodes:
		return Nodes(cls.tree(), cls.resolver())


class TestNode(TestCase):
	def test_full_path(self) -> None:
		nodes = Fixture.nodes()
		root = nodes.by('file_input')
		class_a = nodes.children(root.full_path)[0]
		empty = nodes.children(class_a.full_path)[0]
		block_a = nodes.children(class_a.full_path)[1]

		self.assertEqual(root.full_path, 'file_input')
		self.assertEqual(class_a.full_path, 'file_input.class')
		self.assertEqual(class_a.parent.full_path, 'file_input')
		self.assertEqual(empty.full_path, 'file_input.class.__empty__')
		self.assertEqual(empty.parent.full_path, 'file_input.class')
		self.assertEqual(block_a.full_path, 'file_input.class.block')
		self.assertEqual(block_a.parent.full_path, 'file_input.class')


	@data_provider([
		('file_input', 'file_input'),
		('file_input.class.__empty__', '__empty__'),
		('file_input.class.block', 'block'),
		('file_input.class.block.enum', 'enum'),
		('file_input.class.block.function[1]', 'function'),
		('file_input.class.block.function[2]', 'function'),
		('file_input.function', 'function'),
	])
	def test_tag(self, full_path: str, expected: str) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.tag, expected)


	@data_provider([
		('file_input', '__main__'),
		('file_input.class', '__main__'),
		('file_input.class.__empty__', '__main__'),
		('file_input.class.block', '__main__.Class'),
		('file_input.class.block.enum', '__main__.Class'),
		('file_input.class.block.enum.block', '__main__.Class.Enum'),
		('file_input.class.block.function[1]', '__main__.Class'),
		('file_input.class.block.function[1].block', '__main__.Class'),
		('file_input.class.block.function[1].block.if', '__main__.Class'),
		('file_input.class.block.function[1].block.if.block', '__main__.Class'),
		('file_input.function.block.term_a', '__main__'),
	])
	def test_namespace(self, full_path: str, expected: str) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.namespace, expected)


	@data_provider([
		('file_input', '__main__'),
		('file_input.class', '__main__'),
		('file_input.class.__empty__', '__main__'),
		('file_input.class.block', '__main__.class'),
		('file_input.class.block.enum', '__main__.class'),
		('file_input.class.block.enum.block', '__main__.class.enum'),
		('file_input.class.block.function[1]', '__main__.class'),
		('file_input.class.block.function[1].block', '__main__.class.function'),
		('file_input.class.block.function[1].block.if', '__main__.class.function'),
		('file_input.class.block.function[1].block.if.block', '__main__.class.function.if'),
		('file_input.function.block.term_a', '__main__.function'),
	])
	def test_scope(self, full_path: str, expected: str) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.scope, expected)


	@data_provider([
		('file_input', 0),
		('file_input.class', 0),
		('file_input.class.__empty__', 0),
		('file_input.class.block', 1),
		('file_input.class.block.enum', 1),
		('file_input.class.block.enum.block', 2),
		('file_input.class.block.function[1]', 1),
		('file_input.class.block.function[1].block', 2),
		('file_input.class.block.function[1].block.if', 2),
		('file_input.class.block.function[1].block.if.block', 3),
		('file_input.function.block.term_a', 1),
	])
	def test_nest(self, full_path: str, expected: int) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.nest, expected)


	@data_provider([
		('file_input.class', 'file_input'),
		('file_input.class.__empty__', 'file_input.class'),
		('file_input.class.block.enum', 'file_input.class.block'),
		('file_input.class.block.function[1].block', 'file_input.class.block.function[1]'),
		('file_input.class.block.function[2]', 'file_input.class.block'),
		('file_input.function.block.term_a', 'file_input.function.block'),
	])
	def test_parent(self, full_path: str, expected: str) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.parent.full_path, expected)


	@data_provider([
		('file_input.class', [
			'file_input.class.block',
			'file_input.class.block.enum',
			'file_input.class.block.enum.block.assign[0]',
			'file_input.class.block.enum.block.assign[0].term_a',
			'file_input.class.block.enum.block.assign[1]',
			'file_input.class.block.enum.block.assign[1].term_a',
			'file_input.class.block.function[1]',
			'file_input.class.block.function[1].block',
			'file_input.class.block.function[1].block.if',
			'file_input.class.block.function[1].block.if.block',
			'file_input.class.block.function[1].block.if.block.term_a',
			'file_input.class.block.function[2]',
			'file_input.class.block.function[2].block',
			'file_input.class.block.function[2].block.term_a',
		]),
		('file_input.class.block.enum', [
			'file_input.class.block.enum.block.assign[0]',
			'file_input.class.block.enum.block.assign[0].term_a',
			'file_input.class.block.enum.block.assign[1]',
			'file_input.class.block.enum.block.assign[1].term_a',
		]),
		('file_input.function', [
			'file_input.function.block',
			'file_input.function.block.term_a',
		]),
	])
	def test___iter__(self, full_path: str, expected: list[str]) -> None:
		nodes = Fixture.nodes()
		all = [node.full_path for node in nodes.by(full_path)]
		self.assertEqual(all, expected)


	def test_as_a(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('fule_input.class')
		self.assertEqual(type(node), Class)
		self.assertEqual(type(node.as_a(Terminal)), Terminal)


	def test_is_a(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('fule_input.class')
		self.assertEqual(type(node), Class)
		self.assertEqual(node.is_a(Class), True)
		self.assertEqual(node.is_a(Node), False)
		self.assertEqual(node.is_a(Terminal), False)


	def test_if_not_a_to_b(self) -> None:
		nodes = Fixture.nodes()
		empty = nodes.by('fule_input.class.__empty__')
		self.assertEqual(empty.is_a(Empty), True)
		self.assertEqual(empty.if_not_a_to_b(Empty, Terminal).is_a(Terminal), False)


	def test_actual(self) -> None:
		class NodeB(Node):
			def actualize(self) -> Node:
				return self.as_a(Terminal)


		nodes = Fixture.nodes()
		node = NodeB(nodes, 'node_b')
		self.assertEqual(type(node), NodeB)
		self.assertEqual(type(node.actualize()), Terminal)


	def test___str__(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('file_input')
		self.assertEqual(str(node), '<FileInput: file_input>')
