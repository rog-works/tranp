from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.node import Node


@Meta.embed(Node, accept_tags('group_expr'))
class Group(Node):
	@property
	@Meta.embed(Node, expandable)
	def expression(self) -> Node:
		return self._at(0)


@Meta.embed(Node, accept_tags('star_expr'))
class Spread(Node):
	@property
	@Meta.embed(Node, expandable)
	def expression(self) -> Node:
		return self._at(0)
