from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.primary import Symbol, GenericType
from py2cpp.node.definition.statement_simple import AnnoAssign
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node
from py2cpp.node.trait import ScopeTrait


@Meta.embed(Node, accept_tags('paramvalue'))
class Parameter(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('typedparam.name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Symbol | GenericType | Empty:
		return self._by('typedparam')._at(1).one_of(Symbol | GenericType | Empty)

	@property
	@Meta.embed(Node, expandable)
	def default_value(self) -> Node | Empty:
		node = self._at(1)
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]


@Meta.embed(Node, accept_tags('assign_stmt'))
class Var(Node):
	@property
	def access(self) -> str:
		# XXX
		symbol = self.symbol.to_string()
		if symbol.startswith('__'):
			return 'private'
		elif symbol.startswith('_'):
			return 'protected'
		else:
			return 'public'

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('anno_assign')._at(0).as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Symbol | GenericType:
		return self._by('anno_assign')._at(1).one_of(Symbol | GenericType)

	@property
	@Meta.embed(Node, expandable)
	def initial_value(self) -> Node:
		return self._by('anno_assign')._at(2)


@Meta.embed(Node, accept_tags('block'))
class Block(Node, ScopeTrait):
	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	@property
	def decl_vars(self) -> list[Var]:
		assigns = {node.as_a(AnnoAssign): True for node in reversed(self.statements) if node.is_a(AnnoAssign)}
		return [node.rerole(Var) for node in reversed(assigns.keys())]
