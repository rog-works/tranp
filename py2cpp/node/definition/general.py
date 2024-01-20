from py2cpp.lang.implementation import override
from py2cpp.node.definition.primary import LocalDeclVar
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('file_input'))
class Entrypoint(Node):
	@property
	@override
	def namespace(self) -> str:
		return self.module_path

	@property
	@override
	def scope(self) -> str:
		return self.module_path

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	@property
	def decl_vars(self) -> list[AnnoAssign | MoveAssign]:
		# @see element.Block.decl_vars
		assigns = {
			node.one_of(AnnoAssign | MoveAssign): True
			for node in reversed(self.statements)
			if isinstance(node, (AnnoAssign, MoveAssign)) and node.receiver.is_a(LocalDeclVar)
		}
		return list(reversed(assigns.keys()))
