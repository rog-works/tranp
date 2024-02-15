from rogw.tranp.lang.implementation import implements
from rogw.tranp.node.definition.primary import FuncCall, ImportPath, Indexer, Reference, Declable, Type, Var
from rogw.tranp.node.definition.terminal import Empty, Terminal
from rogw.tranp.node.embed import Meta, accept_tags, expandable
from rogw.tranp.node.interface import ITerminal
from rogw.tranp.node.node import Node
from rogw.tranp.node.promise import IDeclaration


class Assign(Node):
	@property
	@Meta.embed(Node, expandable)
	def receivers(self) -> list[Declable | Reference | Indexer]:
		return [node.one_of(Declable | Reference | Indexer) for node in self._children('assign_namelist')]

	@property
	def _elements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('assign'))
class MoveAssign(Assign, IDeclaration):
	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[1]
		return node if isinstance(node, Empty) else node

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self.receivers]


@Meta.embed(Node, accept_tags('anno_assign'))
class AnnoAssign(Assign, IDeclaration):
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
	@implements
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self.receivers]


@Meta.embed(Node, accept_tags('aug_assign'))
class AugAssign(Assign):
	@property
	@Meta.embed(Node, expandable)
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node:
		return self._elements[2]


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
		# XXX self.parent.as_a(Block).parent.as_a(Function)
		return self.parent.parent


@Meta.embed(Node, accept_tags('raise_stmt'))
class Throw(Node):
	@property
	@Meta.embed(Node, expandable)
	def throws(self) -> FuncCall | Var:
		return self._at(0).one_of(FuncCall | Var)

	@property
	@Meta.embed(Node, expandable)
	def via(self) -> Reference | Empty:
		return self._at(1).one_of(Reference | Empty)


@Meta.embed(Node, accept_tags('pass_stmt'))
class Pass(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Break(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Continue(Node, ITerminal): pass


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node):
	@property
	def import_path(self) -> ImportPath:
		return self._by('dotted_name').as_a(ImportPath)

	@property
	@Meta.embed(Node, expandable)
	def import_symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('import_names')]
