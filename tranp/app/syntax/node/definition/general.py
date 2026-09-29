from typing import override

from tranp.app.dsn.dsn import DSN
from tranp.app.lang.annotation import duck_typed
from tranp.app.syntax.node.definition.primary import DeclLocalVar
from tranp.app.syntax.node.definition.statement_compound import VarsCollector
from tranp.app.syntax.node.definition.statement_simple import Import
from tranp.app.syntax.node.embed import Meta, accept_tags, expandable
from tranp.app.syntax.node.interface import StatementBlock
from tranp.app.syntax.node.node import Node


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
	def scope(self) -> str:
		return self.module_path

	@property
	@override
	def namespace(self) -> str:
		return self.module_path

	@property
	@duck_typed(StatementBlock)
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	@property
	def decl_vars(self) -> list[DeclLocalVar]:
		return VarsCollector.collect(self, DeclLocalVar)

	@property
	def imports(self) -> list[Import]:
		"""Note: XXX インポートは第1階層のみ対象とする。現状は第1階層のみサポートしているため問題ないが検討の余地あり"""
		return [statement for statement in self.statements if isinstance(statement, Import)]

	def whole_by(self, full_path: str) -> Node:
		return self._by(DSN.relativefy(full_path, self.full_path))
