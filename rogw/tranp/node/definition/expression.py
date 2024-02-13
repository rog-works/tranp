from rogw.tranp.node.embed import Meta, accept_tags, expandable
from rogw.tranp.node.node import Node


@Meta.embed(Node, accept_tags('group_expr'))
class Group(Node):
	@property
	@Meta.embed(Node, expandable)
	def expression(self) -> Node:
		return self._at(0)
