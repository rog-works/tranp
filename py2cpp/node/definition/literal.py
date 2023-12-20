from py2cpp.lang.annotation import override
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized
from py2cpp.node.node import Node


class Literal(Node): pass


@Meta.embed(Node, accept_tags('number'))
class Number(Literal):
	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, actualized(via=Number))
class Integer(Number):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['number', 'DEC_NUMBER', 'HEX_NUMBER'])


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
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, accept_tags('key_value'))
class KeyValue(Node):
	@property
	def key(self) -> Node:
		return self._at(0).if_a_actualize_from_b(Terminal, Expression)

	@property
	def value(self) -> Node:
		return self._at(1).if_a_actualize_from_b(Terminal, Expression)


@Meta.embed(Node, accept_tags('list'))
class List(Node):
	@property
	def values(self) -> list[Node]:
		return [node.if_a_actualize_from_b(Terminal, Expression) for node in self._children()]


@Meta.embed(Node, accept_tags('dict'))
class Dict(Node):
	@property
	def items(self) -> list[KeyValue]:
		return [node.as_a(KeyValue) for node in self._children()]
