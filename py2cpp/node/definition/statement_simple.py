from py2cpp.lang.annotation import override
from py2cpp.node.definition.primary import GenericType, Indexer, Symbol
from py2cpp.node.definition.terminal import Empty, Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def _elements(self) -> list[Node]:
		return self._at(0)._children()

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol | Indexer:
		return self._elements[0].one_of(Symbol | Indexer)


@Meta.embed(Node, actualized(via=Assign))
class MoveAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('assign')

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[1]
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, actualized(via=Assign))
class AnnoAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('anno_assign')

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Symbol | GenericType:
		return self._elements[1].one_of(Symbol | GenericType)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[2]
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, actualized(via=Assign))
class AugAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('aug_assign')

	@property
	@Meta.embed(Node, expandable)
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._elements[2]


@Meta.embed(Node, accept_tags('return_stmt'))
class Return(Node):
	@property
	@Meta.embed(Node, expandable)
	def return_value(self) -> Node | Empty:
		node = self._at(0)
		return self.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node):
	@property
	@override
	def is_terminal(self) -> bool:
		return True

	@property
	@Meta.embed(Node, expandable)
	def module_path(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def import_symbols(self) -> list[Symbol]:
		return [node.as_a(Symbol) for node in self._children('import_names')]
