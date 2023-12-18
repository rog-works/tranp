from py2cpp.lang.annotation import override
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.terminal import Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized
from py2cpp.node.node import Node


class Literal(Node): pass


@Meta.embed(Node, accept_tags('primary', 'number'), actualized(via=Expression))
class Integer(Literal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['primary', 'atom', 'number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, accept_tags('primary', 'number'), actualized(via=Expression))
class Float(Literal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['primary', 'atom', 'number', 'FLOAT_NUMBER'])

	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, accept_tags('primary', 'string'), actualized(via=Expression))
class String(Literal):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['primary', 'atom', 'string', 'STRING'])

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
		return self._at(0).as_a(Expression).actualize()

	@property
	def value(self) -> Node:
		return self._at(1).as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('list'))
class List(Node):
	@property
	def values(self) -> list[Node]:
		return [node.as_a(Expression).actualize() for node in self._children()]


@Meta.embed(Node, accept_tags('dict'))
class Dict(Node):
	@property
	def items(self) -> list[KeyValue]:
		return [node.as_a(KeyValue) for node in self._children()]
