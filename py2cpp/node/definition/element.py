from py2cpp.lang.implementation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.primary import DecoratorPath, Declable, Type
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node
from py2cpp.node.promise import IDeclable


@Meta.embed(Node, accept_tags('paramvalue'))
class Parameter(Node, IDeclable):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		"""Note: XXX 実体はBlockVarのみ"""
		return self._by('typedparam.name').as_a(Declable)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type | Empty:
		return self._by('typedparam')._at(1).one_of(Type | Empty)

	@property
	@Meta.embed(Node, expandable)
	def default_value(self) -> Node | Empty:
		node = self._at(1)
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, accept_tags('return_type'))
class ReturnDecl(Node):
	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		return self._at(0).one_of(Type)


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	@Meta.embed(Node, expandable)
	def path(self) -> DecoratorPath:
		return self._by('dotted_name').as_a(DecoratorPath)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')] if self._exists('arguments') else []
