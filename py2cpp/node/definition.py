from typing import cast

from py2cpp.lang.annotation import override
from py2cpp.node.embed import embed_meta, node_properties
from py2cpp.node.node import Node
from py2cpp.node.trait import NamedScopeTrait


class Terminal(Node):
	@property
	def value(self) -> str:
		return ''.join([node.value for node in self._expansion() if isinstance(node, Terminal)])


class Symbol(Terminal):
	@property
	def names(self) -> list[Terminal]:
		return cast(list[Terminal], self._leafs('name'))


	@property
	def symbol(self) -> str:
		return '.'.join([name.value for name in self.names])


class Import(Node):
	@property
	def names(self) -> list[Terminal]:
		return cast(list[Terminal], self._siblings('dotted_name.name'))


	@property
	def module_path(self) -> str:
		return '.'.join([name.value for name in self.names])


class Decorator(Node):
	@property
	def symbol(self) -> Terminal:
		return cast(Terminal, self._by('name'))


	@property
	def arguments(self) -> list[Symbol]:
		return cast(list[Symbol], [node for node in self._siblings('symbol') if type(node) is Symbol])


@embed_meta(node_properties('statements'))
class Class(Node, NamedScopeTrait):
	@property
	@override
	def scope_name(self) -> str:
		return self.class_name.value


	@property
	def decorators(self) -> list[Decorator]:
		return cast(list[Decorator], self._siblings('decorators.decorator'))


	@property
	def class_name(self) -> Terminal:
		return cast(Terminal, self._by('class_def_row.name'))


	@property
	def parents(self) -> list[Symbol]:
		return cast(list[Symbol], [node for node in self._siblings('class_def_row.symbol') if type(node) is Symbol])


	@property
	def statements(self) -> list[Node]:
		return self._children('class_def_row.block.statement')


@embed_meta(node_properties('statements'))
class FileInput(Node):
	@property
	@override
	def namespace(self) -> str:
		return self.scope


	@property
	@override
	def scope(self) -> str:
		return '__main__'  # XXX ファイル名の方が良いのでは


	@property
	def statements(self) -> list[Node]:
		return self._children('statement')
