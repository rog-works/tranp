from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.entry import Entry
from py2cpp.ast.resolver import Settings
from py2cpp.ast.query import Query
from py2cpp.errors import NotFoundError
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Currying, Locator
from py2cpp.module.base import ModulePath
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.tp_lark.entry import EntryOfLark
from tests.test.helper import data_provider


class Root(Node): pass
class TreeA(Node): pass
class TreeB(Node): pass
class TreeC(Node): pass
class TokenA(Node): pass
class TokenB(Node): pass
class TokenC(Node): pass
class Terminal(Node): pass
class Empty(Node): pass


class Fixture:
	@classmethod
	def di(cls) -> DI:
		di = DI()
		di.bind(Locator, lambda: di)
		di.bind(Currying, lambda: di.currying)
		di.bind(Query[Node], Nodes)
		di.bind(NodeResolver, NodeResolver)
		di.bind(ModulePath, lambda: '__main__')
		di.bind(Settings, cls.__settings)
		di.bind(Entry, cls.__tree)
		return di

	@classmethod
	def __tree(cls) -> Entry:
		tree = Tree('root', [
			Tree('tree_a', [
				None,
				Token('token_a', 'a.a'),
				Tree('tree_b', []),
				Tree('tree_b', [
					Token('token_b', 'a.b.b'),
				]),
				Token('token_a', 'a.a'),
				Token('token_c', 'a.c'),
			]),
			Token('term_a', 'a'),
			Tree('tree_c', [
				Tree('skip_tree_a', [
					Token('term_a', 'c.a.a'),
				]),
			]),
		])
		return EntryOfLark(tree)

	@classmethod
	def __settings(cls) -> Settings:
		return Settings(
			symbols={
				'root': Root,
				'tree_a': TreeA,
				'tree_b': TreeB,
				'tree_c': TreeC,
				'token_a': TokenA,
				'token_b': TokenB,
				'token_c': TokenC,
				'__empty__': Empty,
			},
			fallback=Terminal
		)

	@classmethod
	def resolver(cls) -> NodeResolver:
		return cls.di().resolve(NodeResolver)

	@classmethod
	def nodes(cls) -> Query[Node]:
		return cls.di().resolve(Query[Node])


class TestNodeResolver(TestCase):
	@data_provider([
		('root', True),
		('tree_a', True),
		('token_a', True),
		('__empty__', True),
		('skip_tree_a', False),
		('unknown', False),
	])
	def test_can_resolve(self, tag: str, expected: type[Node]) -> None:
		resolver = Fixture.resolver()
		self.assertEqual(resolver.can_resolve(tag), expected)

	def test_resolve(self) -> None:
		resolver = Fixture.resolver()
		self.assertEqual(resolver.resolve('root', 'root').full_path, 'root')


class TestNodes(TestCase):
	@data_provider([
		('root', True),
		('root.tree_a', True),
		('root.tree_a.__empty__', True),
		('root.tree_a.token_a[1]', True),
		('root.tree_a.tree_b[2]', True),
		('root.tree_a.tree_b[3]', True),
		('root.tree_a.tree_b[3].token_b', True),
		('root.tree_a.token_a[4]', True),
		('root.tree_a.token_c', True),
		('root.term_a', True),
		('root.tree_c', True),
		('root.outside', False),
		('path.to.unknown', False),
	])
	def test_exists(self, path: str, expected: bool) -> None:
		nodes = Fixture.nodes()
		self.assertEqual(nodes.exists(path), expected)

	@data_provider([
		('root', Root),
		('root.tree_a', TreeA),
		('root.tree_a.__empty__', Empty),
		('root.tree_a.token_a[1]', TokenA),
		('root.tree_a.tree_b[2]', TreeB),
		('root.tree_a.tree_b[3]', TreeB),
		('root.tree_a.tree_b[3].token_b', TokenB),
		('root.tree_a.token_a[4]', TokenA),
		('root.tree_a.token_c', TokenC),
		('root.term_a', Terminal),
		('root.tree_c', TreeC),
	])
	def test_by(self, path: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		node = nodes.by(path)
		self.assertEqual(type(node), expected)

	@data_provider([
		('root.tree_a', Root),
		('root.tree_a.__empty__', TreeA),
		('root.tree_a.token_a[1]', TreeA),
		('root.tree_a.tree_b[2]', TreeA),
		('root.tree_a.tree_b[3]', TreeA),
		('root.tree_a.tree_b[3].token_b', TreeB),
		('root.tree_a.token_a[4]', TreeA),
		('root.tree_a.token_c', TreeA),
		('root.term_a', Root),
		('root.tree_c.skip_tree_a.term_a', TreeC),
	])
	def test_parent(self, via: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		node = nodes.parent(via)
		self.assertEqual(type(node), expected)

	@data_provider([
		('root.tree_a', 'root', Root),
		('root.tree_a.__empty__', 'tree_a', TreeA),
		('root.tree_a.token_a[1]', 'tree_a', TreeA),
		('root.tree_a.tree_b[2]', 'tree_a', TreeA),
		('root.tree_a.tree_b[3]', 'root', Root),
		('root.tree_a.tree_b[3].token_b', 'tree_a', TreeA),
		('root.tree_a.token_a[4]', 'root', Root),
		('root.tree_a.token_c', 'tree_a', TreeA),
		('root.term_a', 'root', Root),
		('root.tree_c.skip_tree_a.term_a', 'tree_c', TreeC),
	])
	def test_ancestor(self, via: str, tag: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		node = nodes.ancestor(via, tag)
		self.assertEqual(type(node), expected)

	@data_provider([
		('root.tree_a', [TreeA, Terminal, TreeC]),
		('root.tree_a.__empty__', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.tree_a.token_a[1]', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.tree_a.tree_b[2]', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.tree_a.tree_b[3].token_b', [TokenB]),
		('root.tree_a.token_c', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.term_a', [TreeA, Terminal, TreeC]),
	])
	def test_siblings(self, via: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		in_nodes = nodes.siblings(via)
		self.assertEqual([type(node) for node in in_nodes], expected)

	@data_provider([
		('root', [TreeA, Terminal, TreeC]),
		('root.tree_a', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.tree_a.__empty__', []),
		('root.tree_a.token_a[1]', []),
		('root.tree_a.tree_b[2]', []),
		('root.tree_a.tree_b[3]', [TokenB]),
		('root.tree_a.token_c', []),
		('root.term_a', []),
	])
	def test_children(self, via: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		in_nodes = nodes.children(via)
		self.assertEqual([type(node) for node in in_nodes], expected)

	@data_provider([
		('root', [TreeA, Terminal, TreeC]),
		('root.tree_a', [Empty, TokenA, TreeB, TreeB, TokenA, TokenC]),
		('root.tree_a.tree_b[3]', [TokenB]),
		('root.term_a', []),
		('root.tree_c', [Terminal]),
	])
	def test_expand(self, via: str, expected: type[Node]) -> None:
		nodes = Fixture.nodes()
		in_nodes = nodes.expand(via)
		self.assertEqual([type(node) for node in in_nodes], expected)

	@data_provider([
		('root.__empty__', NotFoundError),
	])
	def test_expand_error(self, via: str, expected: type[Exception]) -> None:
		nodes = Fixture.nodes()
		with self.assertRaises(expected):
			nodes.expand(via)

	@data_provider([
		('root.tree_a', ['a.a', 'a.b.b', 'a.a', 'a.c']),
		('root.tree_a.token_a[1]', ['a.a']),
		('root.tree_a.tree_b[3].token_b', ['a.b.b']),
		('root.term_a', ['a']),
		('root.tree_c.skip_tree_a.term_a', ['c.a.a']),
	])
	def test_values(self, via: str, expected: str) -> None:
		nodes = Fixture.nodes()
		self.assertEqual(nodes.values(via), expected)
