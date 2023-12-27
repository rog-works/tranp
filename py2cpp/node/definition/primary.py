import re

from py2cpp.ast.dns import domainize
from py2cpp.lang.annotation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.node import Node
from py2cpp.node.trait import TerminalTrait


@Meta.embed(Node, accept_tags('getattr', 'var', 'name', 'dotted_name', 'typed_getattr', 'typed_var'))
class Symbol(Node, TerminalTrait):
	@property
	def domain_id(self) -> str:
		return domainize(self.scope, self.tokens)

	@property
	def domain_name(self) -> str:
		return domainize(self.module.path, self.tokens)


@Meta.embed(Node, actualized(via=Symbol))
class Var(Symbol):
	"""Note: ローカル変数と引数に対応。クラスメンバーは如何なる種類もこのシンボルにあたらない"""

	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via.tag != 'var':
			return False

		name = via.tokens
		if name == 'self' or name.find('.') != -1:
			return False

		return via.parent.tag != 'getattr'


@Meta.embed(Node, actualized(via=Symbol))
class This(Symbol):
	@property
	@override
	def domain_id(self) -> str:
		return self.namespace

	@property
	@override
	def domain_name(self) -> str:
		return self.domain_id

	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.tokens == 'self'


@Meta.embed(Node, actualized(via=Symbol))
class ThisVar(Symbol):
	@property
	@override
	def domain_id(self) -> str:
		return domainize(self.namespace, self.tokens.split('.')[1])

	@property
	@override
	def domain_name(self) -> str:
		return self.domain_id

	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return re.fullmatch(r'self\.\w+', via.tokens) is not None


@Meta.embed(Node, accept_tags('getitem'))
class Indexer(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)

	@property
	@Meta.embed(Node, expandable)
	def key(self) -> Node:
		return self._by('slices.slice')._at(0)


@Meta.embed(Node, accept_tags('typed_getitem'))
class GenericType(Node):
	@property
	def domain_id(self) -> str:
		return domainize(self.scope, self.symbol.tokens)

	@property
	def domain_name(self) -> str:
		return domainize(self.module.path, self.symbol.tokens)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)


@Meta.embed(Node, actualized(via=GenericType))
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).tokens != 'list':
			return False

		return len(via._by('typed_slices')._children()) == 1

	@property
	@Meta.embed(Node, expandable)
	def value_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, actualized(via=GenericType))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).tokens != 'dict':
			return False

		return len(via._by('typed_slices')._children()) == 2

	@property
	@Meta.embed(Node, expandable)
	def key_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice[0]')._at(0).one_of(Symbol | GenericType)

	@property
	@Meta.embed(Node, expandable)
	def value_type(self) -> Symbol | GenericType:
		return self._by('typed_slices.typed_slice[1]')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, accept_tags('typed_or_expr'))
class UnionType(GenericType):
	@property
	@Meta.embed(Node, expandable)
	def types(self) -> list[Symbol]:  # FIXME GenericTypeにも対応
		return [node.as_a(Symbol) for node in self._children()]


@Meta.embed(Node, accept_tags('funccall'))
class FuncCall(Node):
	@property
	@Meta.embed(Node, expandable)
	def calls(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def arguments(self) -> list[Argument]:
		args = self._at(1)
		return [node.as_a(Argument) for node in args._children()] if not args.is_a(Empty) else []
