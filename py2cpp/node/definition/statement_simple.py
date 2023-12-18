from py2cpp.lang.annotation import override
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.primary import GenericType, Indexer, Symbol
from py2cpp.node.definition.terminal import Empty, Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized, expansionable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def _elements(self) -> list[Node]:
		return self._at(0)._children()

	@property
	def symbol(self) -> Symbol | Indexer:
		return self._elements[0].if_not_a_to_b(Indexer, Symbol)


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class MoveAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('assign')

	@property
	def value(self) -> Node | Empty:
		if self._elements[1].is_a(Empty):
			return self._elements[1].as_a(Empty)

		return self._elements[1].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AnnoAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('anno_assign')

	@property
	def variable_type(self) -> Symbol | GenericType:
		return self._elements[1].if_not_a_to_b(GenericType, Symbol)

	@property
	def value(self) -> Node | Empty:
		if self._elements[2].is_a(Empty):
			return self._elements[2].as_a(Empty)

		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AugAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('aug_assign')

	@property
	def symbol(self) -> Symbol | Indexer:
		return self._elements[0].if_not_a_to_b(Indexer, Symbol)

	@property
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)

	@property
	def value(self) -> Node:
		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('return_stmt'))
class Return(Node):
	@property
	def return_value(self) -> Expression | Empty:
		return self._at(0).if_not_a_to_b(Empty, Expression)


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node):
	@property
	@override
	def is_terminal(self) -> bool:
		return True

	@property
	@Meta.embed(Node, expansionable(order=0))
	def module_path(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expansionable(order=1))
	def import_symbols(self) -> list[Symbol]:
		return [node.as_a(Symbol) for node in self._children('import_names')]
