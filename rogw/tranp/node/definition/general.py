from rogw.tranp.lang.implementation import override
from rogw.tranp.node.definition.primary import DeclLocalVar
from rogw.tranp.node.definition.statement_compound import VarsCollector
from rogw.tranp.node.embed import Meta, accept_tags, expandable
from rogw.tranp.node.node import Node


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
	def decl_vars(self) -> list[DeclLocalVar]:
		return list(VarsCollector.collect(self, DeclLocalVar).values())
