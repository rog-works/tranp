from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.entry import Entry
from py2cpp.ast.resolver import SymbolMapping
from py2cpp.ast.query import Query
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Currying, Locator
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node
from py2cpp.node.query import Nodes
from py2cpp.node.resolver import NodeResolver
from py2cpp.providers.module import module_path_dummy
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
		di.bind(ModulePath, module_path_dummy)
		di.bind(SymbolMapping, cls.__settings)
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
	def __settings(cls) -> SymbolMapping:
		return SymbolMapping(
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
