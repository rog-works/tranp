from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.entry import Entry
from py2cpp.ast.provider import Query, Settings
from py2cpp.lang.annotation import override
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Curry, Locator
from py2cpp.node.embed import Meta, actualized, expandable
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.trait import ScopeTrait
from py2cpp.tp_lark.entry import EntryOfLark
from tests.test.helper import data_provider


class Terminal(Node): pass
class Empty(Node): pass
class Expression(Node): pass
class Assign(Node): pass
class Block(Node, ScopeTrait): pass


class If(Node):
	@property
	@Meta.embed(Node, expandable)
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
	def name(self) -> str:
		return 'C1'

	@property
	@override
	def scope_name(self) -> str:
		return self.name

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class Enum(Node):
	@property
	@override
	def name(self) -> str:
		return 'E1'

	@property
	@override
	def scope_name(self) -> str:
		return self.name

	@property
	@Meta.embed(Node, expandable)
	def vars(self) -> list[Assign]:
		return [node.as_a(Assign) for node in self._children('block')]


class Function(Node):
	@property
	@override
	def name(self) -> str:
		return 'F1'

	@property
	@Meta.embed(Node, expandable)
	def block(self) -> Block:
		return self._by('block').as_a(Block)


class Method(Function): pass


class Fixture:
	@classmethod
	def di(cls) -> DI:
		di = DI()
		di.bind(Locator, lambda: di)
		di.bind(Curry, lambda: di.curry)
		di.bind(Query[Node], Nodes)
		di.bind(NodeResolver, NodeResolver)
		di.bind(Settings, cls.__settings)
		di.bind(Entry, cls.__tree)
		return di

	@classmethod
	def __tree(cls) -> Entry:
		tree = Tree('file_input', [
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
		return EntryOfLark(tree)

	@classmethod
	def __settings(cls) -> Settings:
		return Settings(
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
		)

	@classmethod
	def nodes(cls) -> Query[Node]:
		return cls.di().resolve(Query[Node])


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
		('file_input', 'file_input'),
		('file_input.class.__empty__', 'empty'),
		('file_input.class.block', 'block'),
		('file_input.class.block.enum', 'enum'),
		('file_input.class.block.function[1]', 'function'),
		('file_input.class.block.function[2]', 'function'),
		('file_input.function', 'function'),
	])
	def test_classification(self, full_path: str, expected: str) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(full_path)
		self.assertEqual(node.classification, expected)

	@data_provider([
		('file_input', '__main__'),
		('file_input.class', '__main__'),
		('file_input.class.__empty__', '__main__'),
		('file_input.class.block', '__main__.C1'),
		('file_input.class.block.enum', '__main__.C1'),
		('file_input.class.block.enum.block', '__main__.C1.E1'),
		('file_input.class.block.function[1]', '__main__.C1'),
		('file_input.class.block.function[1].block', '__main__.C1'),
		('file_input.class.block.function[1].block.if', '__main__.C1'),
		('file_input.class.block.function[1].block.if.block', '__main__.C1'),
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
		('file_input.class.block', '__main__.C1'),
		('file_input.class.block.enum', '__main__.C1'),
		('file_input.class.block.enum.block', '__main__.C1.E1'),
		('file_input.class.block.function[1]', '__main__.C1'),
		('file_input.class.block.function[1].block', '__main__.C1.F1'),
		('file_input.class.block.function[1].block.if', '__main__.C1.F1'),
		('file_input.class.block.function[1].block.if.block', '__main__.C1.F1.if'),
		('file_input.function.block.term_a', '__main__.F1'),
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
	def test_flatten(self, full_path: str, expected: list[str]) -> None:
		nodes = Fixture.nodes()
		all = [node.full_path for node in nodes.by(full_path).flatten()]
		self.assertEqual(all, expected)

	@data_provider([
		('file_input.class', [
			'file_input.class.block.enum.block.assign[0].term_a',
			'file_input.class.block.enum.block.assign[0]',
			'file_input.class.block.enum.block.assign[1].term_a',
			'file_input.class.block.enum.block.assign[1]',
			'file_input.class.block.enum',
			'file_input.class.block.function[1].block.if.block.term_a',
			'file_input.class.block.function[1].block.if.block',
			'file_input.class.block.function[1].block.if',
			'file_input.class.block.function[1].block',
			'file_input.class.block.function[1]',
			'file_input.class.block.function[2].block.term_a',
			'file_input.class.block.function[2].block',
			'file_input.class.block.function[2]',
			'file_input.class.block',
		]),
	])
	def test_calculated(self, full_path: str, expected: list[str]) -> None:
		nodes = Fixture.nodes()
		all = [node.full_path for node in nodes.by(full_path).calculated()]
		self.assertEqual(all, expected)

	def test_is_a(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('file_input.class')
		self.assertEqual(type(node), Class)
		self.assertEqual(node.is_a(Class), True)
		self.assertEqual(node.is_a(Node), True)
		self.assertEqual(node.is_a(Terminal), False)

	def test_as_a(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('file_input.class.block.function[1]')
		self.assertEqual(type(node), Function)
		self.assertEqual(type(node.as_a(Method)), Method)

	def test_one_of(self) -> None:
		nodes = Fixture.nodes()
		empty = nodes.by('file_input.class.__empty__')
		self.assertEqual(type(empty), Empty)
		self.assertEqual(type(empty.one_of(Empty)), Empty)
		self.assertEqual(type(empty.one_of(Terminal | Empty)), Empty)

	def test_match_feature(self) -> None:
		class NodeA(Node):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tag == 'node_a'

		di = Fixture.di()
		root = NodeA(di, 'root')
		node = NodeA(di, 'node_a')
		self.assertEqual(NodeA.match_feature(root), False)
		self.assertEqual(NodeA.match_feature(node), True)

	def test_actualize(self) -> None:
		class NodeSet(Node): pass

		@Meta.embed(Node, actualized(via=NodeSet))
		class NodeSubset(NodeSet):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tag == 'node_subset'

		di = Fixture.di()
		node = NodeSet(di, 'node_subset')
		self.assertEqual(type(node), NodeSet)
		self.assertEqual(type(node.actualize()), NodeSubset)

	def test___str__(self) -> None:
		nodes = Fixture.nodes()
		node = nodes.by('file_input')
		self.assertEqual(str(node), '<FileInput: file_input>')
