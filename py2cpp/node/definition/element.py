from py2cpp.lang.implementation import implements
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.literal import Null
from py2cpp.node.definition.primary import GenericType, Symbol
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.base import T_NodeBase
from py2cpp.node.interface import IScope
from py2cpp.node.node import Node


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


@Meta.embed(Node, accept_tags('return_type'))
class ReturnType(Node):
	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Symbol | GenericType | Null:
		return self._at(0).one_of(Symbol | GenericType | Null)


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')] if self._exists('arguments') else []


@Meta.embed(Node, accept_tags('block'))
class Block(Node, IScope):
	@property
	@implements
	def scope_part(self) -> str:
		"""Note: XXX 親が公開名称を持つノード(クラス/ファンクション)の場合は空文字。それ以外は親の一意エントリータグを返却"""
		return '' if self.parent.public_name else self.parent._full_path.elements[-1]

	@property
	@implements
	def namespace_part(self) -> str:
		return ''

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	def decl_vars_with(self, allow: type[T_NodeBase]) -> list[AnnoAssign | MoveAssign]:
		# @see general.Entrypoint.block.decl_vars
		assigns = {
			node.one_of(AnnoAssign | MoveAssign): True
			for node in reversed(self.statements)
			if isinstance(node, (AnnoAssign, MoveAssign)) and node.symbol.is_a(allow)
		}
		return list(reversed(assigns.keys()))
