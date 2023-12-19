from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.primary import Symbol, GenericType
from py2cpp.node.definition.terminal import Empty, Terminal
from py2cpp.node.embed import Meta, accept_tags, expansionable
from py2cpp.node.node import Node
from py2cpp.node.trait import ScopeTrait


@Meta.embed(Node, accept_tags('paramvalue'))
class Parameter(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('typedparam.name').as_a(Symbol)

	@property
	def var_type(self) -> Symbol | GenericType | Empty:
		typed = self._by('typedparam')._at(1)
		if typed.is_a(Empty):
			return typed.as_a(Empty)

		return typed.if_not_a_to_b(GenericType, Symbol)

	@property
	def default_value(self) -> Terminal | Empty:
		return self._at(1).if_not_a_to_b(Empty, Terminal)


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
	def symbol(self) -> Symbol:
		return self._by('anno_assign')._at(0).as_a(Symbol)

	@property
	def var_type(self) -> Symbol | GenericType:
		return self._by('anno_assign')._at(1).if_not_a_to_b(GenericType, Symbol)

	@property
	def initial_value(self) -> Node:
		return self._by('anno_assign')._at(2).if_a_actualize_from_b(Terminal, Expression)


@Meta.embed(Node, accept_tags('block'))
class Block(Node, ScopeTrait):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expansionable(order=0))
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]
