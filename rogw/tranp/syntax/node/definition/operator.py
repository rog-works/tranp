from rogw.tranp.lang.annotation import override
from rogw.tranp.syntax.node.definition.terminal import Terminal
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.node import Node


class Operator(Node): pass


class UnaryOperator(Operator):
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


class BinaryOperator(Operator):
	@property
	@Meta.embed(Node, expandable)
	def elements(self) -> list[Node]:
		return self._children()


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


@Meta.embed(Node, accept_tags('tenary_test'))
class TenaryOperator(Operator):
	@property
	@Meta.embed(Node, expandable)
	def primary(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(1)

	@property
	@Meta.embed(Node, expandable)
	def secondary(self) -> Node:
		return self._at(2)
