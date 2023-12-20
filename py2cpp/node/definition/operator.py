from py2cpp.lang.annotation import override
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, expansionable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('factor'))
class UnaryOperator(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def operator(self) -> Terminal:
		return self._at(0).as_a(Terminal)

	@property
	@Meta.embed(Node, expansionable(order=1))
	def value(self) -> Node:
		return self._at(1).if_a_actualize_from_b(Terminal, Expression)


class BinaryOperator(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def left(self) -> Node:
		return self._at(0).if_a_actualize_from_b(Terminal, Expression)

	@property
	@Meta.embed(Node, expansionable(order=1))
	def operator(self) -> Terminal:
		return self._at(1).as_a(Terminal)

	@property
	@Meta.embed(Node, expansionable(order=2))
	def right(self) -> Node:
		return self._at(2).if_a_actualize_from_b(Terminal, Expression)


@Meta.embed(Node, accept_tags('or_expr'))
class OrBitwise(BinaryOperator): pass


@Meta.embed(Node, accept_tags('xor_expr'))
class XorBitwise(BinaryOperator): pass


@Meta.embed(Node, accept_tags('and_expr'))
class AndBitwise(BinaryOperator): pass


@Meta.embed(Node, accept_tags('shift_expr'))
class ShiftBitwise(BinaryOperator): pass


@Meta.embed(Node, accept_tags('sum'))
class Sum(BinaryOperator): pass


@Meta.embed(Node, accept_tags('term'))
class Term(BinaryOperator): pass


# @Meta.embed(Node, accept_tags('group_expr'))
class Group(Node):  # FIXME impl トランスパイルの性質上必要だが、あると色々と邪魔になる
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return False
