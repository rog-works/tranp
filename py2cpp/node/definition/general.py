from py2cpp.lang.implementation import override
from py2cpp.node.definition.primary import DeclLocalVar
from py2cpp.node.definition.statement_compound import Catch, For, collect_decl_vars
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('file_input'))
class Entrypoint(Node):
	@property
	@override
	def domain_name(self) -> str:
		return self.module_path

	@property
	@override
	def fullyname(self) -> str:
		return self.module_path

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
	def decl_vars(self) -> list[AnnoAssign | MoveAssign | For | Catch]:
		return list(collect_decl_vars(self, DeclLocalVar).values())
