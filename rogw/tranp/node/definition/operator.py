from rogw.tranp.lang.implementation import override
from rogw.tranp.node.definition.terminal import Terminal
from rogw.tranp.node.embed import Meta, accept_tags, expandable
from rogw.tranp.node.node import Node


class UnaryOperator(Node):
	@property
	@override
	def tokens(self) -> str:
		return ''.join(self._values())

	@property
	@Meta.embed(Node, expandable)
	def operator(self) -> Terminal:
		return self._at(0).as_a(Terminal)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._at(1)


class BinaryOperator(Node):
	@property
	@Meta.embed(Node, expandable)
	def left(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def operator(self) -> Terminal:
		return self._at(1).as_a(Terminal)

	@property
	@Meta.embed(Node, expandable)
	def right(self) -> list[Node]:
		return self._children()[2:]


@Meta.embed(Node, accept_tags('factor'))
class Factor(UnaryOperator): pass


@Meta.embed(Node, accept_tags('not_test'))
class NotCompare(UnaryOperator): pass


@Meta.embed(Node, accept_tags('or_test'))
class OrCompare(BinaryOperator): pass


@Meta.embed(Node, accept_tags('and_test'))
class AndCompare(BinaryOperator): pass


@Meta.embed(Node, accept_tags('comparison'))
class Comparison(BinaryOperator): pass


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
