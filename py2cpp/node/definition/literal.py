from py2cpp.lang.annotation import override
from py2cpp.lang.string import snakelize
from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.node import Node


class Literal(Node):
	@property
	def alias_name(self) -> str:
		"""Note: FIXME @__alias__と対応。かなり苦し紛れなので修正を検討"""
		return snakelize(self.__class__.__name__)


@Meta.embed(Node, accept_tags('number'))
class Number(Literal):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expand()])


@Meta.embed(Node, actualized(via=Number))
class Integer(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@override
	def alias_name(self) -> str:
		return 'int'


@Meta.embed(Node, actualized(via=Number))
class Float(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'FLOAT_NUMBER'])


@Meta.embed(Node, accept_tags('string'))
class String(Literal):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expand()])

	@property
	@override
	def alias_name(self) -> str:
		return 'str'


class Boolean(Literal):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expand()])

	@property
	@override
	def alias_name(self) -> str:
		return 'bool'


@Meta.embed(Node, accept_tags('const_true'))
class Truthy(Boolean): pass


@Meta.embed(Node, accept_tags('const_false'))
class Falsy(Boolean): pass


@Meta.embed(Node, accept_tags('key_value'))
class KeyValue(Node):
	@property
	@Meta.embed(Node, expandable)
	def key(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._at(1)


@Meta.embed(Node, accept_tags('list'))
class List(Literal):
	@property
	@Meta.embed(Node, expandable)
	def values(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('dict'))
class Dict(Literal):
	@property
	@Meta.embed(Node, expandable)
	def items(self) -> list[KeyValue]:
		return [node.as_a(KeyValue) for node in self._children()]


@Meta.embed(Node, accept_tags('const_none', 'typed_none'))
class Null(Literal): pass
