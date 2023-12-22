from py2cpp.lang.annotation import override
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('file_input'))
class Module(Node):
	@property
	@override
	def scopr_name(self) -> str:
		return '__main__'

	@property
	@override
	def namespace(self) -> str:
		return '__main__'

	@property
	@override
	def scope(self) -> str:
		return '__main__'

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()
