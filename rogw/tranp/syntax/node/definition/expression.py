from typing import override

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.syntax.node.behavior import IDomain
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


@Meta.embed(Node, accept_tags('lambdadef'))
class Lambda(Node, IDomain):
	@property
	@override
	def domain_name(self) -> str:
		# XXX 一意な名称を持たないためIDで代用
		return ModuleDSN.identify(self.classification, self.id)

	@property
	@Meta.embed(Node, expandable)
	def expression(self) -> Node:
		return self._at(0)
