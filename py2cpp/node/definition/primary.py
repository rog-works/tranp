from py2cpp.lang.annotation import override
from py2cpp.node.definition.common import Argument
from py2cpp.node.embed import Meta, accept_tags, actualized, expansionable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('getattr', 'var', 'name', 'dotted_name'))
class Symbol(Node):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, actualized(via=Symbol))
class This(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.to_string().startswith('self')


@Meta.embed(Node, accept_tags('getitem'))
class GetItem(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def symbol(self) -> Symbol:  # FIXME シンボル以外も有り得るので不正確
		return self._at(0).as_a(Symbol)


@Meta.embed(Node, actualized(via=GetItem))
class Indexer(GetItem):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのケースを除外 XXX 定数化
		if via.parent.identifer in ['anno_assign', 'parameter']:
			return False

		return len(via._children('slices')) == 1

	@property
	@Meta.embed(Node, expansionable(order=1))
	def key(self) -> Node:
		return self._by('slices.slice')._at(0)


class GenericType(GetItem): pass


@Meta.embed(Node, actualized(via=GetItem))
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのため、代入か仮引数の場合のみ XXX 定数化
		if via.parent.identifer not in ['anno_assign', 'parameter']:
			return False

		if via._at(0).to_string() != 'list':
			return False

		return len(via._children('slices')) == 1

	@property
	@Meta.embed(Node, expansionable(order=1))
	def value_type(self) -> Symbol | GenericType:
		return self._by('slices.slice')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, actualized(via=GetItem))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# タイプヒントのため、代入か仮引数の場合のみ XXX 定数化
		if via.parent.identifer not in ['anno_assign', 'parameter']:
			return False

		if via._at(0).to_string() != 'dict':
			return False

		return len(via._children('slices')) == 2

	@property
	@Meta.embed(Node, expansionable(order=1))
	def key_type(self) -> Symbol | GenericType:
		return self._by('slices.slice[0]')._at(0).one_of(Symbol | GenericType)

	@property
	@Meta.embed(Node, expansionable(order=2))
	def value_type(self) -> Symbol | GenericType:
		return self._by('slices.slice[1]')._at(0).one_of(Symbol | GenericType)


@Meta.embed(Node, accept_tags('funccall'))
class FuncCall(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def calls(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expansionable(order=1))
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]
