from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


class UnaryOperator(Node):
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
	def right(self) -> Node:
		return self._at(2)


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


@Meta.embed(Node, accept_tags('group_expr'))
class Group(Node): pass  # FIXME impl トランスパイルの性質上必要だが、あると色々と邪魔になる
