import re

from py2cpp.lang.annotation import override
from py2cpp.node.embed import Meta, accept_tags, actualized, expansionable
from py2cpp.node.node import Node
from py2cpp.node.trait import ScopeTrait


class Terminal(Node):
	@classmethod
	def match_terminal(cls, via: Node, allow_tags: list[str]) -> bool:  # XXX
		rel_paths = [node._full_path.relativefy(via.full_path) for node in via.flatten()]
		for rel_path in rel_paths:
			if not rel_path.consists_of_only(*allow_tags):
				return False

		return True


@Meta.embed(Node, accept_tags('__empty__', 'const_none'))
class Empty(Node): pass


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


class Expression(Node): pass


@Meta.embed(Node, accept_tags('primary', 'number'), actualized(via=Expression))
class Integer(Node):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['primary', 'atom', 'number', 'DEC_NUMBER', 'HEX_NUMBER'])

	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, accept_tags('primary', 'number'), actualized(via=Expression))
class Float(Node):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['primary', 'atom', 'number', 'FLOAT_NUMBER'])

	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, accept_tags('getattr', 'primary', 'var', 'name', 'argvalue', 'dotted_name'), actualized(via=Expression))
class Symbol(Node):
	@classmethod
	def match_feature(cls, via: Node) -> bool:
		return Terminal.match_terminal(via, allow_tags=['getattr', 'primary', 'var', 'name', 'NAME'])

	@property
	@override
	def is_terminal(self) -> bool:  # XXX Terminalへの移設を検討
		return True

	@override
	def to_string(self) -> str:  # XXX Terminalへの移設を検討
		return '.'.join([node.to_string() for node in self._under_expansion()])


@Meta.embed(Node, actualized(via=Symbol))
class Self(Symbol):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.to_string().startswith('self')


@Meta.embed(Node, accept_tags('getitem'))
class GetItem(Node):
	@property
	def symbol(self) -> Symbol:
		return self._at(0).as_a(Symbol)


# @Meta.embed(Node, actualized(via=Expression))
class Indexer(GetItem):
	@property
	def key(self) -> Node:
		return self._by('slices').as_a(Expression).actualize()


class GenericType(GetItem): pass


@Meta.embed(Node, actualized(via=GetItem))
class ListType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).to_string() != 'list':
			return False

		return len(via._children('slices')) == 1

	@property
	def value_type(self) -> GenericType:
		return self._by('slices')._at(0).as_a(GenericType)


@Meta.embed(Node, actualized(via=GetItem))
class DictType(GenericType):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).to_string() != 'dict':
			return False

		return len(via._children('slices')) == 2

	@property
	def key_type(self) -> GenericType:
		return self._by('slices')._at(0).as_a(GenericType)

	@property
	def value_type(self) -> GenericType:
		return self._by('slices')._at(1).as_a(GenericType)


@Meta.embed(Node, accept_tags('argvalue'))
class Argument(Node):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def value(self) -> Node:
		return self.as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('funccall'))
class FuncCall(Node):
	@property
	def symbol(self) -> Symbol:  # FIXME 厳密に言うとCallable？関数の戻り値でも良いのでSymbolよりExpressionの方に近い
		return self._at(0).as_a(Symbol)

	@property
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]


@Meta.embed(Node, accept_tags('paramvalue'))
class Parameter(Node):
	@property
	def param_symbol(self) -> Symbol:
		return self._by('typedparam.name').as_a(Symbol)

	@property
	def param_type(self) -> Symbol | Empty:
		return self._by('typedparam')._at(1).if_not_a_to_b(Empty, Symbol)

	@property
	def default_value(self) -> Terminal | Empty:
		return self._at(1).if_not_a_to_b(Empty, Terminal)


@Meta.embed(Node, accept_tags('key_value'))
class KeyValue(Node):
	@property
	def key(self) -> Node:
		return self._at(0).as_a(Expression).actualize()

	@property
	def value(self) -> Node:
		return self._at(1).as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('dict'))
class Dict(Node):
	@property
	def items(self) -> list[KeyValue]:
		return [node.as_a(KeyValue) for node in self._children()]


@Meta.embed(Node, accept_tags('list'))
class List(Node):
	@property
	def values(self) -> list[Node]:
		return [node.as_a(Expression).actualize() for node in self._children()]


@Meta.embed(Node, accept_tags('assign_stmt'))
class Assign(Node):
	@property
	def _elements(self) -> list[Node]:
		return self._at(0)._children()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class MoveAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('assign')

	@property
	def symbol(self) -> Symbol:  # FIXME Symbol | Indexer
		return self._elements[0].as_a(Symbol)

	@property
	def value(self) -> Node:  # FIXME Node | Empty
		return self._elements[1].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AnnoAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('anno_assign')

	@property
	def symbol(self) -> Symbol:  # FIXME Symbol | Indexer
		return self._elements[0].as_a(Symbol)

	@property
	def variable_type(self) -> Symbol:
		return self._elements[1].as_a(Symbol)

	@property
	def value(self) -> Node:  # FIXME Node | Empty
		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'), actualized(via=Assign))
class AugAssign(Assign):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via._exists('aug_assign')

	@property
	def symbol(self) -> Symbol:  # FIXME Symbol | Indexer
		return self._elements[0].as_a(Symbol)

	@property
	def operator(self) -> Terminal:
		return self._elements[1].as_a(Terminal)

	@property
	def value(self) -> Node:
		return self._elements[2].as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('assign_stmt'))
class Variable(Node):
	@property
	def access(self) -> str:
		# XXX
		symbol = self.symbol.to_string()
		if symbol.startswith('__'):
			return 'private'
		elif symbol.startswith('_'):
			return 'protected'
		else:
			return 'public'

	@property
	def symbol(self) -> Symbol:
		return self._by('anno_assign')._at(0).as_a(Symbol)

	@property
	def variable_type(self) -> Symbol:
		return self._by('anno_assign')._at(1).as_a(Symbol)

	@property
	def initial_value(self) -> Node:
		return self._by('anno_assign')._at(2).as_a(Expression).actualize()


@Meta.embed(Node, accept_tags('import_stmt'))
class Import(Node):
	@property
	def module_path(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	def import_symbols(self) -> list[Symbol]:
		return [node.as_a(Symbol) for node in self._children('import_names')]


@Meta.embed(Node, accept_tags('block'))
class Block(Node, ScopeTrait):
	@property
	@Meta.embed(Node, expansionable(order=0))
	def statements(self) -> list[Node]:
		return self._children()


@Meta.embed(Node, accept_tags('if_stmt'))
class If(Node): pass


@Meta.embed(Node, accept_tags('decorator'))
class Decorator(Node):
	@property
	def symbol(self) -> Symbol:
		return self._by('dotted_name').as_a(Symbol)

	@property
	@Meta.embed(Node, expansionable(order=0))
	def arguments(self) -> list[Argument]:
		return [node.as_a(Argument) for node in self._children('arguments')]


@Meta.embed(Node, accept_tags('function_def'))
class Function(Node):
	@property
	def access(self) -> str:
		name = self.function_name.to_string()
		# XXX 定数化などが必要
		if re.fullmatch(r'__.+__', name):
			return 'public'
		elif name.startswith('__'):
			return 'private'
		elif name.startswith('_'):
			return 'protected'
		else:
			return 'public'

	@property
	def function_name(self) -> Terminal:
		return self._by('function_def_raw.name').as_a(Terminal)

	@property
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	def parameters(self) -> list[Parameter]:
		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters')]

	@property
	def return_type(self) -> Symbol | Empty:
		node = self._by('function_def_raw')._at(2)
		return node._by('const_none').as_a(Empty) if node._exists('const_none') else node.as_a(Symbol)

	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)


@Meta.embed(Node, actualized(via=Function))
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return via.as_a(Function).function_name.to_string() == '__init__'

	@property
	def class_name(self) -> Terminal:
		return self.parent.as_a(Block).parent.as_a(Class).class_name  # FIXME 循環参照

	@property
	def decl_variables(self) -> list[Variable]:
		assigns = [node.as_a(AnnoAssign) for node in self.block._children() if node.is_a(AnnoAssign)]
		variables = {node.as_a(Variable): True for node in assigns if node.symbol.is_a(Self)}
		return list(variables.keys())


@Meta.embed(Node, actualized(via=Function))
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		decorators = via.as_a(Function).decorators
		return len(decorators) > 0 and decorators[0].symbol.to_string() == 'classmethod'

	@property
	def class_name(self) -> Terminal:
		return self.parent.as_a(Block).parent.as_a(Class).class_name  # FIXME 循環参照


@Meta.embed(Node, actualized(via=Function))
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		# XXX コンストラクターを除外
		if via.as_a(Function).function_name.to_string() == '__init__':
			return False

		parameters = via.as_a(Function).parameters
		return len(parameters) > 0 and parameters[0].param_symbol.to_string() == 'self'  # XXX 手軽だが不正確

	@property
	def class_name(self) -> Terminal:
		return self.parent.as_a(Block).parent.as_a(Class).class_name  # FIXME 循環参照


@Meta.embed(Node, accept_tags('class_def'))
class Class(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.class_name.to_string()

	@property
	def class_name(self) -> Terminal:
		return self._by('class_def_raw.name').as_a(Terminal)

	@property
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	def parents(self) -> list[Symbol]:
		parents = self._by('class_def_raw')._at(1)
		if parents.is_a(Empty):
			return []

		return [node.as_a(Argument).value.as_a(Symbol) for node in parents._children()]

	@property
	def constructor_exists(self) -> bool:
		candidates = [node.as_a(Constructor) for node in self.block._children() if node.is_a(Constructor)]
		return len(candidates) == 1

	@property
	def constructor(self) -> Constructor:
		return [node.as_a(Constructor) for node in self.block._children() if node.is_a(Constructor)].pop()

	@property
	def class_methods(self) -> list[ClassMethod]:
		return [node.as_a(ClassMethod) for node in self.block._children() if node.is_a(ClassMethod)]

	@property
	def methods(self) -> list[Method]:
		return [node.as_a(Method) for node in self.block._children() if node.is_a(Method)]

	@property
	@Meta.embed(Node, expansionable(order=0))
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)

	@property
	def variables(self) -> list[Variable]:
		return self.constructor.decl_variables if self.constructor_exists else []


@Meta.embed(Node, accept_tags('enum_def'))
class Enum(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.enum_name.to_string()

	@property
	def enum_name(self) -> Terminal:
		return self._by('name').as_a(Terminal)

	@property
	@Meta.embed(Node, expansionable(order=0))
	def variables(self) -> list[MoveAssign]:  # XXX 理想としてはVariableだが、Enumの変数に型の定義がないため一旦MoveAssignで妥協
		return [node.as_a(MoveAssign) for node in self._children('block')]
