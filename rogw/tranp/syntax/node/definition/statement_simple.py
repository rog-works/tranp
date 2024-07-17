from rogw.tranp.lang.annotation import duck_typed, override
from rogw.tranp.syntax.node.behavior import ITerminal
from rogw.tranp.syntax.node.definition.primary import FuncCall, ImportAsName, ImportPath, Reference, Declable, Type, Var
from rogw.tranp.syntax.node.definition.terminal import Empty, Terminal
from rogw.tranp.syntax.node.embed import Meta, accept_tags, expandable
from rogw.tranp.syntax.node.interface import IDeclaration
from rogw.tranp.syntax.node.node import Node


class Assign(Node):
	@property
	def receivers(self) -> list[Declable | Reference]:
		return [node.one_of(Declable, Reference) for node in self._children('assign_namelist')]

	@property
	def _elements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('assign'))
class MoveAssign(Assign, IDeclaration):
	@property
	@override
	@Meta.embed(Node, expandable)
	def receivers(self) -> list[Declable | Reference]:
		return super().receivers

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[1]
		return node if isinstance(node, Empty) else node

	@property
	@duck_typed
	def symbols(self) -> list[Declable]:
		return [node for node in self.receivers if isinstance(node, Declable)]


@Meta.embed(Node, accept_tags('anno_assign'))
class AnnoAssign(Assign, IDeclaration):
	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> Declable:
		return super().receivers[0].as_a(Declable)

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		return self._elements[1].one_of(Type)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[2]
		return node if isinstance(node, Empty) else node

	@property
	@duck_typed
	def symbols(self) -> list[Declable]:
		return [self.receiver]


@Meta.embed(Node, accept_tags('aug_assign'))
class AugAssign(Assign):
	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> Declable | Reference:
		return super().receivers[0]

	@property
	@Meta.embed(Node, expandable)
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._elements[2]


@Meta.embed(Node, accept_tags('del_stmt'))
class Delete(Node):
	@property
	@Meta.embed(Node, expandable)
	def targets(self) -> list[Reference]:
		return [node.as_a(Reference) for node in self._children()]


@Meta.embed(Node, accept_tags('return_stmt'))
class Return(Node):
	@property
	@Meta.embed(Node, expandable)
	def return_value(self) -> Node | Empty:
		node = self._at(0)
		return node if isinstance(node, Empty) else node

	@property
	def function(self) -> Node:
		"""Note: XXX 参照違反になるためNode型で返却"""
		return self._ancestor('function_def')


@Meta.embed(Node, accept_tags('yield_stmt'))
class Yield(Node):
	@property
	@Meta.embed(Node, expandable)
	def yield_value(self) -> Node:
		return self._at(0)

	@property
	def function(self) -> Node:
		"""Note: XXX 参照違反になるためNode型で返却"""
		return self._ancestor('function_def')


@Meta.embed(Node, accept_tags('raise_stmt'))
class Throw(Node):
	@property
	@Meta.embed(Node, expandable)
	def throws(self) -> FuncCall | Var:
		return self._at(0).one_of(FuncCall, Var)

	@property
	@Meta.embed(Node, expandable)
	def via(self) -> Reference | Empty:
		return self._at(1).one_of(Reference, Empty)


@Meta.embed(Node, accept_tags('pass_stmt'))
class Pass(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Break(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Continue(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('comment_stmt'))
class Comment(Node, ITerminal):
	@property
	def text(self) -> str:
		return self.tokens[1:]


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node, IDeclaration):
	@property
	def import_path(self) -> ImportPath:
		return self._by('dotted_name').as_a(ImportPath)

	@property
	@duck_typed
	@Meta.embed(Node, expandable)
	def symbols(self) -> list[ImportAsName]:
		return [node.as_a(ImportAsName) for node in self._children('import_as_names')]
