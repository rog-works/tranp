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
			@override
			def to_string(self) -> str:
				return self._full_path.origin.split('.')[-1]

			@property
			def b_in_a(self) -> NodeA:
				return NodeA(nodes, 'root.node_z.tree.node_b.node_a')

		class NodeZ(Node):
			@property
			def a(self) -> NodeA:
				return NodeA(nodes, 'root.node_z.node_a')

			@property
			def b(self) -> NodeB:
				return NodeB(nodes, 'root.node_z.node_b')

			@property
			def values(self) -> list[Node]:
				return [NodeA(nodes, 'root.node_z.tree.node_a'), NodeB(nodes, 'root.node_z.tree.node_b')]

		T_NodeB = TypedDict('T_NodeB', {'b_in_a': str})
		T_NodeZ = TypedDict('T_NodeZ', {'a': str, 'b': T_NodeB, 'values': list[str]})

		node = NodeZ(nodes, 'root.node_b')
		dump = serialize(node, T_NodeZ)
		self.assertEqual(dump['a'], 'node_a')
		self.assertEqual(dump['b']['b_in_a'], 'node_a')
		self.assertEqual(dump['values'][0], 'node_a')
		self.assertEqual(dump['values'][1], 'node_b')
