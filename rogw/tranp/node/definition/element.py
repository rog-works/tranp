from rogw.tranp.lang.implementation import implements
from rogw.tranp.node.definition.primary import Argument, DecoratorPath, Declable, Type
from rogw.tranp.node.definition.terminal import Empty
from rogw.tranp.node.embed import Meta, accept_tags, expandable
from rogw.tranp.node.node import Node
from rogw.tranp.node.promise import IDeclaration, ISymbol


@Meta.embed(Node, accept_tags('paramvalue', 'starparam'))
class Parameter(Node, IDeclaration, ISymbol):
	"""Note: XXX starparamを受け入れるが、正式に対応する必要がないため通常の引数と同じように扱う"""

	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		"""Note: XXX 実体はDeclBlockVarのみ"""
		return self._by('typedparam.name').as_a(Declable)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type | Empty:
		return self._children('typedparam')[1].one_of(Type | Empty)

	@property
	@Meta.embed(Node, expandable)
	def default_value(self) -> Node | Empty:
		children = self._children()
		if len(children) == 2:
			node = self._at(1)
			return node if isinstance(node, Empty) else node

		# XXX starparamはデフォルト引数がないためダミーを生成
		return self.dirty_child(Empty, '__empty__', tokens='')

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]

	@property
	@implements
	def declare(self) -> 'Parameter':
		return self


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
