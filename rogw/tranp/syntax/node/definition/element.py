from rogw.tranp.lang.annotation import implements
from rogw.tranp.syntax.node.definition.primary import Argument, DeclParam, DecoratorPath, Type
from rogw.tranp.syntax.node.definition.terminal import Empty
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.interface import IDeclaration, ISymbol
from rogw.tranp.syntax.node.node import Node


@Meta.embed(Node, accept_tags('paramvalue', 'starparam', 'kwparams'))
class Parameter(Node, IDeclaration, ISymbol):
	"""
	Note:
		* FIXME starparam/kwparamsを受け入れるが、現状は通常の引数と同様に扱う。一部の関数で必要になるため対処が必要
		* XXX ParameterにIDomainは実装しない(=domain_nameの実装) ※symbolと完全参照名が同じになってしまうため
	"""

	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbol(self) -> DeclParam:
		return self._by('typedparam.name').as_a(DeclParam)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type | Empty:
		children = self._children('typedparam')
		if len(children) > 1:
			return children[1].one_of(Type, Empty)

		return self._by('typedparam').dirty_child(Empty, '__empty__', tokens='')

	@property
	@Meta.embed(Node, expandable)
	def default_value(self) -> Node | Empty:
		children = self._children()
		if len(children) == 2:
			return self._at(1)

		return self.dirty_child(Empty, '__empty__', tokens='')

	@property
	@implements
	def symbols(self) -> list[DeclParam]:
		return [self.symbol]

	@property
	@implements
	def declare(self) -> 'Parameter':
		return self

	@property
	def annotation(self) -> Node | Empty:
		children = self._children('typedparam')
		if len(children) == 3:
			return children[2]

		return self._by('typedparam').dirty_child(Empty, '__empty__', tokens='')


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	@Meta.embed(Node, expandable)
	def path(self) -> DecoratorPath:
		return self._by('dotted_name').as_a(DecoratorPath)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		if not self._exists('arguments'):
			return []

		return [node for node in self._children('arguments') if isinstance(node, Argument)]
