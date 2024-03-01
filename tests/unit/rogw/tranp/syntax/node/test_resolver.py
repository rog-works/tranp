from unittest import TestCase

import lark

from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.resolver import SymbolMapping
from rogw.tranp.syntax.ast.query import Query
from rogw.tranp.lang.di import DI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.syntax.node.query import Nodes
from rogw.tranp.syntax.node.resolver import NodeResolver
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
