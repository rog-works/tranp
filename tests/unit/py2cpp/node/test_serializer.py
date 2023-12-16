from typing import TypedDict
from unittest import TestCase

from lark import Tree

from py2cpp.lang.annotation import override
from py2cpp.node.node import Node
from py2cpp.node.nodes import Nodes, NodeResolver
from py2cpp.node.provider import Resolver
from py2cpp.node.serializer import serialize


class Fixture:
	@classmethod
	def nodes(cls) -> Nodes:
		return Nodes(Tree('root', []), NodeResolver(Resolver[Node]()))


class TestSerializer(TestCase):
	def test_serialize(self) -> None:
		nodes = Fixture.nodes()

		class NodeA(Node):
			@override
			def to_string(self) -> str:
				return self._full_path.origin.split('.')[-1]

		class NodeB(Node):
			@property
			def a(self) -> NodeA:
				return NodeA(nodes, 'root.node_b.node_a')

			@property
			def values(self) -> list[NodeA]:
				return [NodeA(nodes, 'root.node_b.tree.node_a[0]'), NodeA(nodes, 'root.node_b.tree.node_a[1]')]
		
		T_NodeA = TypedDict('T_NodeA', {'a': str, 'values': list[str]})

		node = NodeB(nodes, 'root.node_b')
		dump = serialize(node, T_NodeA)
		self.assertEqual(dump['a'], 'node_a')
		self.assertEqual(dump['values'][0], 'node_a[0]')
		self.assertEqual(dump['values'][1], 'node_a[1]')