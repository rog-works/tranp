from py2cpp.lang.implementation import implements, override
from py2cpp.node.definition.primary import FuncCall, ImportPath, Indexer, Reference, Declable, Type
from py2cpp.node.definition.terminal import Empty, Terminal
from py2cpp.node.embed import Meta, accept_tags, actualized, expandable
from py2cpp.node.interface import ITerminal
from py2cpp.node.node import Node


@Meta.embed(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def _elements(self) -> list[Node]:
		return self._at(0)._children()

	@property
	@Meta.embed(Node, expandable)
	def receiver(self) -> Declable | Reference | Indexer:
		return self._elements[0].one_of(Declable | Reference | Indexer)

	@property
	def symbol(self) -> Declable:
		"""
		Note:
			XXX MoveAssign/AnnoAssign/Parameterのインターフェイスを統一するために定義
			XXX receiverがSymbol以外のインスタンスで使用するとエラーが発生する
			XXX シンボルテーブル作成時以外に使用しないと言う前提
		"""
		return self._elements[0].as_a(Declable)


@Meta.embed(Node, actualized(via=Assign))
class MoveAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('assign')

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[1]
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, actualized(via=Assign))
class AnnoAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('anno_assign')

	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		return self._elements[1].one_of(Type)

	@property
	@Meta.embed(Node, expandable)
	def value(self) -> Node | Empty:
		node = self._elements[2]
		return node.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, actualized(via=Assign))
class AugAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('aug_assign')

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
		return self.as_a(Empty) if node.is_a(Empty) else node


@Meta.embed(Node, accept_tags('raise_stmt'))
class Throw(Node):
	@property
	@Meta.embed(Node, expandable)
	def calls(self) -> FuncCall:
		return self._at(0).as_a(FuncCall)

	@property
	@Meta.embed(Node, expandable)
	def via(self) -> Reference | Empty:
		return self._at(1).one_of(Reference | Empty)


@Meta.embed(Node, accept_tags('pass_stmt'))
class Pass(Node): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Break(Node): pass


@Meta.embed(Node, accept_tags('break_stmt'))
class Continue(Node): pass


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node, ITerminal):
	@property
	@implements
	def can_expand(self) -> bool:
		return False

	@property
	def import_path(self) -> ImportPath:
		return self._by('dotted_name').as_a(ImportPath)

	@property
	def import_symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('import_names')]
