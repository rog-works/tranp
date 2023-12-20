from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._at(0)
