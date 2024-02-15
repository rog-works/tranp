from typing import Generic

from rogw.tranp.compatible.python.embed import __actual__, __alias__
from rogw.tranp.lang.implementation import implements, override
from rogw.tranp.lang.sequence import last_index_of, flatten
from rogw.tranp.node.definition.accessor import to_access
from rogw.tranp.node.definition.element import Decorator, Parameter
from rogw.tranp.node.definition.literal import Comment, Pair, String
from rogw.tranp.node.definition.primary import CustomType, DeclClassVar, DeclLocalVar, Declable, InheritArgument, DeclThisParam, DeclThisVar, Type, TypesName
from rogw.tranp.node.definition.statement_simple import AnnoAssign, MoveAssign
from rogw.tranp.node.definition.terminal import Empty
from rogw.tranp.node.embed import Meta, accept_tags, actualized, expandable
from rogw.tranp.node.interface import IDomain, IScope
from rogw.tranp.node.node import Node
from rogw.tranp.node.promise import IDeclaration, ISymbol, StatementBlock


@Meta.embed(Node, accept_tags('block'))
class Block(Node):
	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()


class Flow(Node): pass


class FlowEnter(Flow, IScope):
	@property
	@implements
	def scope_part(self) -> str:
		return self.classification

	@property
	@implements
	def namespace_part(self) -> str:
		return ''


class FlowPart(Flow): pass


@Meta.embed(Node, accept_tags('elif_'))
class ElseIf(FlowPart):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('if_stmt'))
class If(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def else_ifs(self) -> list[ElseIf]:
		return [node.as_a(ElseIf) for node in self._by('elifs')._children()]

	@property
	@Meta.embed(Node, expandable)
	def else_statements(self) -> list[Node]:
		block = self.else_block
		return block.statements if isinstance(block, Block) else []
	
	@property
	def block(self) -> Block:
		return self._at(1).as_a(Block)

	@property
	def else_block(self) -> Block | Empty:
		return self._at(3).one_of(Block | Empty)

	@property
	def having_blocks(self) -> list[Block]:
		blocks: list[Block] = [self.block]
		for else_if in self.else_ifs:
			blocks.append(else_if.block)

		if isinstance(self.else_block, Block):
			blocks.append(self.else_block)

		return blocks


@Meta.embed(Node, accept_tags('while_stmt'))
class While(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node:
		return self._at(0)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('for_in', 'comp_for_in'))
class ForIn(FlowPart):
	@property
	@Meta.embed(Node, expandable)
	def iterates(self) -> Node:
		return self._at(0)


@Meta.embed(Node, accept_tags('for_stmt'))
class For(FlowEnter, IDeclaration):
	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('for_namelist')]

	@property
	@Meta.embed(Node, expandable)
	def for_in(self) -> ForIn:
		return self._by('for_in').as_a(ForIn)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	def iterates(self) -> Node:
		return self.for_in.iterates

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('except_clause'))
class Catch(FlowPart, IDeclaration):
	@property
	@Meta.embed(Node, expandable)
	def var_type(self) -> Type:
		"""Note: XXX Pythonの仕様では複数の型を捕捉できるが一旦単数で実装"""
		return self._at(0).as_a(Type)

	@property
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		"""Note: XXX Pythonの仕様では省略出来るが実装を簡単にするため必須で実装"""
		return self._by('name').one_of(Declable)

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)


@Meta.embed(Node, accept_tags('try_stmt'))
class Try(FlowEnter):
	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self.block.statements

	@property
	@Meta.embed(Node, expandable)
	def catches(self) -> list[Catch]:
		return [node.as_a(Catch) for node in self._by('except_clauses')._children()]

	@property
	def block(self) -> Block:
		return self._by('block').as_a(Block)

	@property
	def having_blocks(self) -> list[Block]:
		return [self.block, *[catch.block for catch in self.catches]]


@Meta.embed(Node, accept_tags('comp_for'))
class CompFor(Node, IDeclaration):
	"""Note: XXX カテゴリーはExpressionなので、定義位置を再検討"""

	@property
	@implements
	@Meta.embed(Node, expandable)
	def symbols(self) -> list[Declable]:
		return [node.as_a(Declable) for node in self._children('for_namelist')]

	@property
	@Meta.embed(Node, expandable)
	def for_in(self) -> ForIn:
		return self._by('comp_for_in').as_a(ForIn)

	@property
	def iterates(self) -> Node:
		return self.for_in.iterates


class Comprehension(Node):
	@property
	def fors(self) -> list[CompFor]:
		return [node.as_a(CompFor) for node in self._children('comprehension.comp_fors')]

	@property
	def condition(self) -> Node | Empty:
		node = self._children('comprehension')[2]
		return node if isinstance(node, Empty) else node


@Meta.embed(Node, accept_tags('list_comp'))
class ListComp(Comprehension):
	"""Note: XXX カテゴリーはExpressionなので、定義位置を再検討"""

	@property
	@Meta.embed(Node, expandable)
	def projection_value(self) -> Node:
		return self._children('comprehension')[0]

	@property
	@override
	@Meta.embed(Node, expandable)
	def fors(self) -> list[CompFor]:
		return super().fors

	@property
	@Meta.embed(Node, expandable)
	def condition(self) -> Node | Empty:
		return super().condition


@Meta.embed(Node, accept_tags('dict_comp'))
class DictComp(Comprehension):
	"""Note: XXX カテゴリーはExpressionなので、定義位置を再検討"""

	@property
	@Meta.embed(Node, expandable)
	def projection_key(self) -> Node:
		return self._by('comprehension.key_value').as_a(Pair).first

	@property
	@Meta.embed(Node, expandable)
	def projection_value(self) -> Node:
		return self._by('comprehension.key_value').as_a(Pair).second

	@property
	@override
	@Meta.embed(Node, expandable)
	def fors(self) -> list[CompFor]:
		return super().fors

	@property
	@override
	@Meta.embed(Node, expandable)
	def condition(self) -> Node | Empty:
		return super().condition


class ClassDef(Node, IDomain, IScope, IDeclaration, ISymbol):
	@property
	@override
	def domain_name(self) -> str:
		return self.symbol.tokens

	@property
	@override
	def fullyname(self) -> str:
		"""Note: XXX スコープが自身を表すためスコープをそのまま返却"""
		return self.scope

	@property
	@implements
	def scope_part(self) -> str:
		return self.domain_name

	@property
	@implements
	def namespace_part(self) -> str:
		return ''

	@property
	@implements
	def symbols(self) -> list[Declable]:
		return [self.symbol]

	@property
	@implements
	def symbol(self) -> Declable:
		raise NotImplementedError()

	@property
	@implements
	def declare(self) -> 'ClassDef':
		return self

	@property
	def access(self) -> str:
		return to_access(self.symbol.tokens)

	@property
	def decorators(self) -> list[Decorator]:
		return []

	@property
	def comment(self) -> Comment | Empty:
		found_comment = [statement for statement in self._org_statements if isinstance(statement, Comment)]
		if len(found_comment):
			return found_comment.pop()

		return self.dirty_child(Empty, '__empty__', tokens='')

	@property
	def statements(self) -> list[Node]:
		return [statement for statement in self._org_statements if not statement.is_a(Comment)]

	@property
	def _org_statements(self) -> list[Node]:
		return self.block.statements

	@property
	def block(self) -> Block:
		raise NotImplementedError()

	@property
	def generic_types(self) -> list[Type]:
		return []

	@property
	def actual_symbol(self) -> str | None:
		return self._attr_symbol(__actual__.__name__)

	@property
	def alias_symbol(self) -> str | None:
		return self._attr_symbol(__alias__.__name__)

	def _attr_symbol(self, identifier: str) -> str | None:
		"""デコレーターで設定した別名をシンボル名として取り込む

		Args:
			identifier (str): 識別名
		Returns:
			str | None: 別名
		Examples:
			```python
			@__actual__('int')
			class Integer: ...
			```
		"""
		decorators = self.decorators
		if len(decorators) == 0:
			return None

		decorator = decorators[0]
		if not decorator.path.tokens == identifier:
			return None

		return decorator.arguments[0].value.as_a(String).plain

	def _decl_vars_with(self, allow: type[Declable]) -> dict[str, Declable]:
		return collect_decl_vars(self, allow)


@Meta.embed(Node, accept_tags('function_def'))
class Function(ClassDef):
	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		symbol = self._by('function_def_raw.name').as_a(Declable)
		alias = self.actual_symbol
		return symbol if not alias else symbol.dirty_proxify(tokens=alias).as_a(Declable)

	@property
	@override
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	@Meta.embed(Node, expandable)
	def parameters(self) -> list[Parameter]:
		if not self._exists('function_def_raw.parameters'):
			return []

		return [node.as_a(Parameter) for node in self._children('function_def_raw.parameters') if not node.is_a(Empty)]

	@property
	@Meta.embed(Node, expandable)
	def return_type(self) -> Type:
		return self._children('function_def_raw.return_type')[0].as_a(Type)

	@property
	@override
	@Meta.embed(Node, expandable)
	def comment(self) -> Comment | Empty:
		return super().comment

	@property
	@override
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return super().statements

	@property
	@override
	def block(self) -> Block:
		return self._by('function_def_raw.block').as_a(Block)

	@property
	def decl_vars(self) -> list[Parameter | Declable]:
		parameters = self.parameters
		parameter_names = [parameter.symbol.tokens for parameter in parameters]
		local_vars = [var for name, var in self._decl_vars_with(DeclLocalVar).items() if name not in parameter_names]
		return [*parameters, *local_vars]


@Meta.embed(Node, actualized(via=Function))
class ClassMethod(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		decorators = via.decorators
		return len(decorators) > 0 and decorators[0].path.tokens == 'classmethod'

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)


@Meta.embed(Node, actualized(via=Function))
class Constructor(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		return via.symbol.tokens == '__init__'

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)

	@property
	def this_vars(self) -> list[Declable]:
		return list(self._decl_vars_with(DeclThisVar).values())


@Meta.embed(Node, actualized(via=Function))
class Method(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		if via.symbol.tokens == '__init__':
			return False

		parameters = via.parameters
		return len(parameters) > 0 and parameters[0].symbol.is_a(DeclThisParam)

	@property
	def class_types(self) -> ClassDef:
		return self.parent.as_a(Block).parent.as_a(ClassDef)


@Meta.embed(Node, actualized(via=Function))
class Closure(Function):
	@classmethod
	@override
	def match_feature(cls, via: Function) -> bool:
		elems = via._full_path.de_identify().elements
		actual_function_def_at = last_index_of(elems, 'function_def_raw')
		expect_function_def_at = max(0, len(elems) - 3)
		in_decl_function = actual_function_def_at == expect_function_def_at
		return in_decl_function

	@property
	def binded_this(self) -> bool:
		"""Note: メソッド内のクロージャーは、メソッドの所有インスタンスを静的に束縛しているものとして扱う"""
		found_own_class = 'class_def' in self._full_path.de_identify().elements
		if not found_own_class:
			return False

		types = self._ancestor('class_def').as_a(Class)
		own_method_at = len(types.block._full_path.elements) + 1
		own_method = self
		while own_method_at < len(own_method._full_path.elements):
			own_method = own_method.parent

		return own_method.is_a(Constructor, Method)


@Meta.embed(Node, accept_tags('class_def'))
class Class(ClassDef):
	@property
	@override
	def namespace_part(self) -> str:
		return self.domain_name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		symbol = self._by('class_def_raw.name').as_a(Declable)
		alias = self.actual_symbol
		return symbol if not alias else symbol.dirty_proxify(tokens=alias).as_a(Declable)

	@property
	@override
	@Meta.embed(Node, expandable)
	def decorators(self) -> list[Decorator]:
		return [node.as_a(Decorator) for node in self._children('decorators')] if self._exists('decorators') else []

	@property
	@Meta.embed(Node, expandable)
	def inherits(self) -> list[Type]:
		"""Note: XXX Genericは継承チェーンを考慮する必要がないため除外する"""
		return [inherit for inherit in self.__org_inherits if inherit.type_name.tokens != Generic.__name__]

	@property
	@override
	@Meta.embed(Node, expandable)
	def generic_types(self) -> list[Type]:
		candidates = [inherit.as_a(CustomType) for inherit in self.__org_inherits if inherit.type_name.tokens == Generic.__name__]
		return candidates[0].template_types if len(candidates) == 1 else []

	@property
	@override
	@Meta.embed(Node, expandable)
	def comment(self) -> Comment | Empty:
		return super().comment

	@property
	@override
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return super().statements

	@property
	@override
	def block(self) -> Block:
		return self._by('class_def_raw.block').as_a(Block)

	@property
	def __org_inherits(self) -> list[Type]:
		if not self._exists('class_def_raw.typed_arguments'):
			return []

		return [node.as_a(InheritArgument).class_type for node in self._children('class_def_raw.typed_arguments')]

	@property
	def constructor_exists(self) -> bool:
		candidates = [node.as_a(Constructor) for node in self.statements if node.is_a(Constructor)]
		return len(candidates) == 1

	@property
	def constructor(self) -> Constructor:
		return [node.as_a(Constructor) for node in self.statements if node.is_a(Constructor)].pop()

	@property
	def class_methods(self) -> list[ClassMethod]:
		return [node.as_a(ClassMethod) for node in self.statements if node.is_a(ClassMethod)]

	@property
	def methods(self) -> list[Method]:
		return [node.as_a(Method) for node in self.statements if node.is_a(Method)]

	@property
	def class_vars(self) -> list[Declable]:
		return list(self._decl_vars_with(DeclClassVar).values())

	@property
	def this_vars(self) -> list[Declable]:
		return self.constructor.this_vars if self.constructor_exists else []


@Meta.embed(Node, actualized(via=Class))
class Enum(Class):
	@classmethod
	@override
	def match_feature(cls, via: Class) -> bool:
		# XXX CEnumの継承に依存するのは微妙なので、修正を検討
		return 'CEnum' in [inherit.type_name.tokens for inherit in via.inherits]

	@property
	def vars(self) -> list[Declable]:
		# XXX collect_decl_varsだと不要な変数宣言まで拾う可能性があるため、ステートメントから直接収集
		return list(flatten([node.symbols for node in self.statements if isinstance(node, MoveAssign)]))


@Meta.embed(Node, accept_tags('class_assign'))
class AltClass(ClassDef):
	@property
	@override
	def namespace_part(self) -> str:
		return self.domain_name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		return self._by('assign_namelist.var.name').dirty_child(TypesName, '', class_types=self)

	@property
	@Meta.embed(Node, expandable)
	def actual_type(self) -> Type:
		return self._at(1).as_a(Type)


@Meta.embed(Node, accept_tags('template_assign'))
class TemplateClass(ClassDef):
	@property
	@override
	def namespace_part(self) -> str:
		return self.domain_name

	@property
	@override
	@Meta.embed(Node, expandable)
	def symbol(self) -> Declable:
		return self._by('assign_namelist.var.name').dirty_child(TypesName, '', class_types=self)

	@property
	@override
	@Meta.embed(Node, expandable)
	def constraints(self) -> Type | Empty:
		return self._at(2).one_of(Type | Empty)


def collect_decl_vars(block: StatementBlock, allow: type[Declable]) -> dict[str, Declable]:
	def merged_by(decl_vars: dict[str, Declable], declare: IDeclaration) -> dict[str, Declable]:
		allow_vars = {symbol.tokens: symbol for symbol in declare.symbols if isinstance(symbol, allow)}
		return merged(decl_vars, allow_vars)

	def merged(decl_vars: dict[str, Declable], allow_vars: dict[str, Declable]) -> dict[str, Declable]:
		return {**decl_vars, **{key: symbol for key, symbol in allow_vars.items() if key not in decl_vars}}

	decl_vars: dict[str, Declable] = {}
	for node in block.statements:
		if isinstance(node, (AnnoAssign, MoveAssign)):
			decl_vars = merged_by(decl_vars, node)
		if isinstance(node, For):
			decl_vars = merged_by(decl_vars, node)
		elif isinstance(node, Try):
			for catch in node.catches:
				decl_vars = merged_by(decl_vars, catch)
		if isinstance(node, (If, Try)):
			for in_block in node.having_blocks:
				decl_vars = merged(decl_vars, collect_decl_vars(in_block, allow))
		elif isinstance(node, (While, For)):
			decl_vars = merged(decl_vars, collect_decl_vars(node.block, allow))

	return decl_vars
