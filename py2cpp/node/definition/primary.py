from py2cpp.lang.annotation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.definition.terminal import Empty
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('getattr', 'var', 'name', 'dotted_name', 'typed_getattr', 'typed_var'))
class Symbol(Node):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expand()])


@Meta.embed(Node, actualized(via=Symbol))
class This(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.to_string().startswith('self')


@Meta.embed(Node, accept_tags('getitem', 'typed_getitem'))
class GetItem(Node):
	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)


@Meta.embed(Node, actualized(via=GetItem))
class Indexer(GetItem):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via.tag != 'getitem':
			return False

		# タイプヒントのケースを除外 XXX 定数化
		if via.parent.identifer in ['anno_assign', 'parameter', 'function', 'class_method', 'method']:
			return False

		return len(via._children('slices')) == 1

	@property
	@Meta.embed(Node, expandable)
	def key(self) -> Node:
		return self._by('slices.slice')._at(0)


class GenericType(GetItem): pass


@Meta.embed(Node, actualized(via=GetItem))
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのため、代入・仮引数・戻り値の場合のみ XXX 定数化
		if via.parent.identifer not in ['anno_assign', 'parameter', 'function', 'class_method', 'method']:
			return False

		if via._at(0).to_string() != 'list':
			return False

		# XXX _at(1) -> slices | typed_slices
		return len(via._at(1)._children()) == 1

	@property
	@Meta.embed(Node, expandable)
	def value_type(self) -> Symbol | GenericType:
		# XXX _at(1)._at(0) -> slices.slice | typed_slices.typed_slice
		return self._at(1)._at(0)._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, actualized(via=GetItem))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのため、代入・仮引数・戻り値の場合のみ XXX 定数化
		if via.parent.identifer not in ['anno_assign', 'parameter', 'function', 'class_method', 'method']:
			return False

		if via._at(0).to_string() != 'dict':
			return False

		# XXX _at(1) -> slices | typed_slices
		return len(via._at(1)._children()) == 2

	@property
	@Meta.embed(Node, expandable)
	def key_type(self) -> Symbol | GenericType:
		# XXX _at(1)._at(0) -> slices.slice[0] | typed_slices.typed_slice[0]
		return self._at(1)._at(0)._at(0).one_of(Symbol | GenericType)

	@property
	@Meta.embed(Node, expandable)
	def value_type(self) -> Symbol | GenericType:
		# XXX _at(1)._at(1) -> slices.slice[1] | typed_slices.typed_slice[1]
		return self._at(1)._at(1)._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, actualized(via=GetItem))
class UnionType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのため、代入・仮引数・戻り値の場合のみ XXX 定数化
		if via.parent.identifer not in ['anno_assign', 'parameter', 'function', 'class_method', 'method']:
			return False

		return via._exists('or_expr')

	@property
	@Meta.embed(Node, expandable)
	def types(self) -> list[Symbol]:  # XXX GenericTypeにも対応するかどうか
		return [node.as_a(Symbol) for node in self._by('or_bitwise')._children()]


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
