from typing import cast

from py2cpp.ast.dsn import DSN
from py2cpp.lang.annotation import implements, override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.literal import Literal
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, ITerminal
from py2cpp.node.node import Node
from py2cpp.node.protocol import Symbolization


@Meta.embed(Node, accept_tags('getattr', 'var', 'name', 'dotted_name', 'typed_getattr', 'typed_var'))
class Symbol(Node, IDomainName, ITerminal):
	@property
	@implements
	def can_expand(self) -> bool:
		return False

	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.tokens)


@Meta.embed(Node, actualized(via=Symbol))
class SymbolRelay(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Symbol) -> bool:
		if via.tag != 'getattr':
			return False

		allow_tags = ['getattr', 'var', 'name']
		receiver_tag = via._at(0).tag
		symbol_tag = via._at(1).tag
		return receiver_tag not in allow_tags and symbol_tag in allow_tags

	@property
	@implements
	def can_expand(self) -> bool:
		return True

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'FuncCall | Indexer | Literal':  # XXX 前方参照
		return self._at(0).one_of(FuncCall | Indexer | Literal)

	@property
	def property(self) -> Symbol:
		"""Note: receiverと不可分な要素であり、単体で解釈不能なため展開対象から除外"""
		return self._at(1).as_a(Symbol)


@Meta.embed(Node, actualized(via=Symbol))
class Var(Symbol):
	"""Note: ローカル変数と引数に対応。クラスメンバーは如何なる種類もこのシンボルにあたらない"""

	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via.tag not in ['var', 'name']:
			return False

		parent_tag = via._full_path.shift(-1).last_tag
		if parent_tag == 'getattr':
			return False

		name = via.tokens
		return name != 'self' and name.find('.') == -1


@Meta.embed(Node, actualized(via=Symbol))
class This(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.tag in ['var', 'name'] and via.tokens == 'self'

	@property
	def class_types(self) -> Node:
		# XXX 中途半端感があるので修正を検討
		return self._ancestor('class_def')


@Meta.embed(Node, actualized(via=Symbol))
class ThisVar(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via.tag != 'getattr':
			return False

		return via.tokens.startswith('self.')

	@property
	@override
	def domain_id(self) -> str:
		return DSN.join(cast(IDomainName, self.class_types).domain_id, self.tokens_without_this)

	@property
	@override
	def domain_name(self) -> str:
		return DSN.join(cast(IDomainName, self.class_types).domain_name, self.tokens_without_this)

	@property
	def tokens_without_this(self) -> str:
		return self.tokens.replace('self.', '')

	@property
	def class_types(self) -> Node:
		# XXX 中途半端感があるので修正を検討
		return self._ancestor('class_def')


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
class GenericType(Node, IDomainName):
	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.symbol.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.symbol.tokens)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)


class CollectionType(GenericType):
	@property
	def value_type(self) -> Symbol | GenericType:
		raise NotImplementedError()


@Meta.embed(Node, actualized(via=GenericType))
class ListType(CollectionType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).tokens != 'list':
			return False

		return len(via._by('typed_slices')._children()) == 1

	@property
	@override
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
	@override
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


@Meta.embed(Node, actualized(via=FuncCall))
class Super(FuncCall):
	@classmethod
	@override
	def match_feature(cls, via: FuncCall) -> bool:
		return via.calls.tokens == 'super'

	@property
	def class_symbol(self) -> Symbol:
		return cast(Symbolization, self._ancestor('class_def')).symbol.as_a(Symbol)
