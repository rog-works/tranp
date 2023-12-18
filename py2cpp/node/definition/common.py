from py2cpp.node.definition.expression import Expression
from py2cpp.node.embed import Meta, accept_tags, expansionable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def value(self) -> Node:
		return self._at(0).as_a(Expression).actualize()
