from typing import cast

from py2cpp.ast.dsn import DSN
from py2cpp.lang.implementation import implements, override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.literal import Literal
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import IDomainName, ITerminal
from py2cpp.node.node import Node
from py2cpp.node.protocol import Symbolization


@Meta.embed(Node, accept_tags('getattr', 'var', 'name', 'dotted_name', 'typed_getattr', 'typed_var'))
class Fragment(Node):
	@property
	def parent_tag(self) -> str:
		return self._full_path.shift(-1).last_tag


@Meta.embed(Node, accept_tags('getattr', 'typed_getattr'), actualized(via=Fragment))
class SymbolRelay(Fragment):
	@classmethod
	@override
	def match_feature(cls, via: Fragment) -> bool:
		return via.parent_tag in ['getattr', 'typed_getattr']

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> 'Fragment | FuncCall | Indexer | Literal':  # XXX 前方参照
		return self._at(0).one_of(Fragment | FuncCall | Indexer | Literal)

	@property
	def property(self) -> Fragment:
		"""Note: receiverと不可分な要素であり、単体で解釈不能なため展開対象から除外"""
		return self._at(1).as_a(Fragment)


class Symbol(Fragment, IDomainName):
	@property
	@implements
	def domain_id(self) -> str:
		return DSN.join(self.scope, self.tokens)

	@property
	@implements
	def domain_name(self) -> str:
		return DSN.join(self.module_path, self.tokens)


@Meta.embed(Node, accept_tags('getattr', 'var', 'name'), actualized(via=Fragment))
class ThisVar(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Fragment) -> bool:
		return via.parent_tag != 'getattr' and via.tokens.startswith('self')

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
		return DSN.join(*DSN.elements(self.tokens)[1:])

	@property
	def class_types(self) -> Node:
		# XXX 中途半端感があるので修正を検討
		return self._ancestor('class_def')


@Meta.embed(Node, accept_tags('getattr', 'var', 'name'), actualized(via=Fragment))
class Var(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Fragment) -> bool:
		return via.parent_tag != 'getattr' and not via.tokens.startswith('self')


@Meta.embed(Node, accept_tags('typed_getattr', 'typed_var'), actualized(via=Fragment))
class TypeSymbol(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Fragment) -> bool:
		return via.parent_tag != 'typed_getattr'


@Meta.embed(Node, accept_tags('name', 'dotted_name'), actualized(via=Fragment))
class SymbolName(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Fragment) -> bool:
		return via.parent_tag not in ['var', 'dotted_name', 'typed_var']


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
