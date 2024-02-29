from unittest import TestCase

import lark

from rogw.tranp.ast.entry import Entry
from rogw.tranp.ast.resolver import SymbolMapping
from rogw.tranp.ast.query import Query
from rogw.tranp.errors import NotFoundError
from rogw.tranp.lang.di import DI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.types import ModulePath
from rogw.tranp.node.node import Node
from rogw.tranp.node.query import Nodes
from rogw.tranp.node.resolver import NodeResolver
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.test.helper import data_provider
from rogw.tranp.tp_lark.entry import EntryOfLark


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
		di.bind(Invoker, lambda: di.invoke)
		di.bind(Query[Node], Nodes)
		di.bind(NodeResolver, NodeResolver)
		di.bind(ModulePath, module_path_dummy)
		di.bind(SymbolMapping, cls.__settings)
		di.bind(Entry, cls.__tree)
		return di

	@classmethod
	def __tree(cls) -> Entry:
		tree = lark.Tree('root', [
			lark.Tree('tree_a', [
				None,
				lark.Token('token_a', 'a.a'),
				lark.Tree('tree_b', []),
				lark.Tree('tree_b', [
					lark.Token('token_b', 'a.b.b'),
				]),
				lark.Token('token_a', 'a.a'),
				lark.Token('token_c', 'a.c'),
			]),
			lark.Token('term_a', 'a'),
			lark.Tree('tree_c', [
				lark.Tree('skip_tree_a', [
					lark.Token('term_a', 'c.a.a'),
				]),
			]),
		])
		return EntryOfLark(tree)

	@classmethod
	def __settings(cls) -> SymbolMapping:
		return SymbolMapping(
			symbols={
				Root: ['root'],
				TreeA: ['tree_a'],
				TreeB: ['tree_b'],
				TreeC: ['tree_c'],
				TokenA: ['token_a'],
				TokenB: ['token_b'],
				TokenC: ['token_c'],
				Empty: ['__empty__'],
			},
			fallback=Terminal
		)

	@classmethod
	def resolver(cls) -> NodeResolver:
		return cls.di().resolve(NodeResolver)

	@classmethod
	def nodes(cls) -> Query[Node]:
		return cls.di().resolve(Query[Node])


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
