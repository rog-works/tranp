from py2cpp.lang.annotation import override
from py2cpp.node.embed import Meta, accept_tags, expansionable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('file_input'))
class FileInput(Node):
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
	@Meta.embed(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()
