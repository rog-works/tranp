from typing import override
from unittest import TestCase

import rogw.tranp.syntax.node.definition as defs  # XXX テストを拡充するため実装クラスを使用
from rogw.tranp.syntax.node.node import Node, T_Node
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestNode(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__)

	@data_provider([
		('...', 'file_input', '<Entrypoint: @0 __main__ (1, 1)..(2, 1)>'),
		('class A: ...', 'file_input.class_def', '<Class: @1 __main__#A (1, 1)..(2, 1)>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: @1 __main__#func (1, 1)..(2, 1)>'),
	])
	def test___str__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(str(node), expected)

	@data_provider([
		('...', 'file_input', '<Entrypoint: __main__ file_input>'),
		('class A: ...', 'file_input.class_def', '<Class: __main__ file_input.class_def>'),
		('def func() -> None: ...', 'file_input.function_def', '<Function: __main__ file_input.function_def>'),
	])
	def test___repr__(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.__repr__(), expected)

	@data_provider([
		('...', 'file_input', 'file_input', True),
		('class A: ...', 'file_input.class_def', 'file_input.class_def', True),
		('class A: ...', 'file_input', 'file_input.class_def', False),
	])
	def test___eq__(self, source: str, full_path_a: str, full_path_b: str, expected: bool) -> None:
		node_a = self.fixture.custom_nodes_by(source, full_path_a)
		node_b = self.fixture.custom_nodes_by(source, full_path_b)
		self.assertEqual(node_a == node_b, expected)

	@data_provider([
		('...', 'file_input', '__main__'),
		('class A: ...', 'file_input.class_def', '__main__'),
		('def func() -> None: ...', 'file_input.function_def', '__main__'),
	])
	def test_module_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.module_path, expected)

	@data_provider([
		('...', 'file_input', 'file_input'),
		('class A: ...', 'file_input.class_def', 'file_input.class_def'),
		('def func() -> None: ...', 'file_input.function_def', 'file_input.function_def'),
	])
	def test_full_path(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.full_path, expected)

	@data_provider([
		('...', 'file_input', 'file_input'),
		('class A: ...', 'file_input.class_def', 'class_def'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'block'),
		('class E(Enum): ...', 'file_input.class_def', 'class_def'),
		('def func() -> None: ...', 'file_input.function_def', 'function_def'),
		('if 1: ...', 'file_input.if_stmt', 'if_stmt'),
		('1', 'file_input.number', 'number'),
		('[a for a in []]', 'file_input.list_comp', 'list_comp'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', 'dict_comp'),
	])
	def test_tag(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.tag, expected)

	@data_provider([
		('...', 'file_input', 'entrypoint'),
		('class A: ...', 'file_input.class_def', 'class'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'block'),
		('class E(Enum): ...', 'file_input.class_def', 'enum'),
		('def func() -> None: ...', 'file_input.function_def', 'function'),
		('if 1: ...', 'file_input.if_stmt', 'if'),
		('1', 'file_input.number', 'integer'),
		('[a for a in []]', 'file_input.list_comp', 'list_comp'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', 'dict_comp'),
	])
	def test_classification(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.classification, expected)

	@data_provider([
		# General
		('...', 'file_input', defs.Entrypoint, '__main__', '__main__'),
		# Statement compound - Block
		('if True: ...', 'file_input.if_stmt.if_clause.block', defs.Block, '', '__main__#if@1.if_clause@2.block@4'),
		# Statement compound - Flow
		('if True: ...', 'file_input.if_stmt', defs.If, 'if@1', '__main__#if@1'),
		('if True: ...\nelif True: ...', 'file_input.if_stmt.elif_clauses.elif_clause', defs.ElseIf, 'else_if@7', '__main__#if@1.else_if@7'),
		('if True: ...\nelse: ...', 'file_input.if_stmt.else_clause', defs.Else, 'else@7', '__main__#if@1.else@7'),
		('while True: ...', 'file_input.while_stmt', defs.While, 'while@1', '__main__#while@1'),
		('for i in [0]: ...', 'file_input.for_stmt', defs.For, 'for@1', '__main__#for@1'),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt', defs.Try, 'try@1', '__main__#try@1'),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', defs.Catch, 'catch@6', '__main__#try@1.catch@6'),
		('with open(a) as f: ...', 'file_input.with_stmt', defs.With, 'with@1', '__main__#with@1'),
		# Statement compound - ClassDef
		('def func() -> None: ...', 'file_input.function_def', defs.Function, 'func', '__main__#func'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.ClassMethod, 'c_method', '__main__#A.c_method'),
		('class A:\n\tdef __init__(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Constructor, '__init__', '__main__#A.__init__'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def', defs.Method, 'method', '__main__#A.method'),
		('class A:\n\tdef method(self) -> None:\n\t\tdef closure() -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.function_def', defs.Closure, 'closure', '__main__#A.method.closure'),
		('class A: ...', 'file_input.class_def', defs.Class, 'A', '__main__#A'),
		('class E(Enum): ...', 'file_input.class_def', defs.Enum, 'E', '__main__#E'),
		('B: TypeAlias = A', 'file_input.class_assign', defs.AltClass, 'B', '__main__#B'),
		('T = TypeVar("T")', 'file_input.template_assign', defs.TemplateClass, 'T', '__main__#T'),
		# Elements
		('def func(n: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue', defs.Parameter, '', '__main__#func.parameter@7'),
		('@deco\ndef func(n: int) -> None: ...', 'file_input.function_def.decorators.decorator', defs.Decorator, '', '__main__#func.decorator@3'),
		# Statement simple - Assign
		('a = 0', 'file_input.assign', defs.MoveAssign, '', '__main__#move_assign@1'),
		('a: int = 0', 'file_input.anno_assign', defs.AnnoAssign, '', '__main__#anno_assign@1'),
		('a += 1', 'file_input.aug_assign', defs.AugAssign, '', '__main__#aug_assign@1'),
		('del a', 'file_input.del_stmt', defs.Delete, '', '__main__#delete@1'),
		# Statement simple - Other
		('def func() -> int:\n\treturn 0', 'file_input.function_def.function_def_raw.block.return_stmt', defs.Return, '', '__main__#func.return@11'),
		('def func() -> Iterator[int]:\n\tyield 0', 'file_input.function_def.function_def_raw.block.yield_stmt', defs.Yield, '', '__main__#func.yield@16'),
		('raise Exception()', 'file_input.raise_stmt', defs.Throw, '', '__main__#throw@1'),
		('pass', 'file_input.pass_stmt', defs.Pass, '', '__main__#pass@1'),
		('break', 'file_input.break_stmt', defs.Break, '', '__main__#break@1'),
		('continue', 'file_input.continue_stmt', defs.Continue, '', '__main__#continue@1'),
		('# abc', 'file_input.comment_stmt', defs.Comment, '', '__main__#comment@1'),
		('from a.b.c import A', 'file_input.import_stmt', defs.Import, '', '__main__#import@1'),
		# Primary - Argument
		('a(0)', 'file_input.funccall.arguments.argvalue', defs.Argument, '', '__main__#argument@6'),
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue', defs.InheritArgument, '', '__main__#B.inherit_argument@7'),  # XXX Typeと同じでは？
		('a(n=0)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel, '', '__main__#argument_label@7'),
		# Primary - Var
		('class A:\n\ta: ClassVar[int] = 0', 'file_input.class_def.class_def_raw.block.class_var_assign.assign_namelist.var', defs.DeclClassVar, 'a', '__main__#A.a'),
		('class A:\n\ta: int', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclThisVarForward, 'a', '__main__#A.a'),
		('class A:\n\tdef __init__(self) -> None:\n\t\tself.a: int = 0', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign.assign_namelist.getattr', defs.DeclThisVar, 'a', '__main__#A.a'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam, 'cls', '__main__#A.c_method.cls'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam, 'self', '__main__#A.method.self'),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar, 'i', '__main__#for@1.i'),
		('try:\n\ta\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar, 'e', '__main__#try@1.catch@8.e'),
		('with open(a) as f: ...', 'file_input.with_stmt.with_items.with_item.name', defs.DeclLocalVar, 'f', '__main__#with@1.f'),
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar, 'a', '__main__#a'),
		('[a for a in []]', 'file_input.list_comp.comprehension.comp_fors.comp_for.for_namelist.name', defs.DeclLocalVar, 'a', '__main__#list_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[0]', defs.DeclLocalVar, 'a', '__main__#dict_comp@1.a'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[1]', defs.DeclLocalVar, 'b', '__main__#dict_comp@1.b'),
		# Primary - Name
		('class A: ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, 'A', '__main__#A.A'),
		('B: TypeAlias = A', 'file_input.class_assign.assign_namelist.var', defs.AltTypesName, 'B', '__main__#B.B'),
		('from a.b.c import A', 'file_input.import_stmt.import_as_names.import_as_name.name', defs.ImportName, 'A', '__main__#A'),
		('from a.b.c import A as B', 'file_input.import_stmt.import_as_names.import_as_name.name[0]', defs.ImportName, 'A', '__main__#A'),
		('from a.b.c import A as B', 'file_input.import_stmt.import_as_names.import_as_name.name[1]', defs.ImportName, 'B', '__main__#B'),
		('from a.b.c import A', 'file_input.import_stmt.import_as_names.import_as_name', defs.ImportAsName, 'A', '__main__#A'),
		('from a.b.c import A as B', 'file_input.import_stmt.import_as_names.import_as_name', defs.ImportAsName, 'B', '__main__#B'),
		# Primary - Reference
		('a.b', 'file_input.getattr', defs.Relay, 'a.b', '__main__#a.b'),
		('{"a": 1}.items()', 'file_input.funccall.getattr', defs.Relay, 'dict@3.items', '__main__#dict@3.items'),
		('a[0].items()', 'file_input.funccall.getattr', defs.Relay, 'items', '__main__#items'),  # XXX Indexerに名前は不要ではあるが一意性が無くて良いのか検討
		('if True:\n\tif True:\n\t\ta.b', 'file_input.if_stmt.if_clause.block.if_stmt.if_clause.block.getattr', defs.Relay, 'a.b', '__main__#if@1.if_clause@2.if@5.if_clause@6.a.b'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None:\n\t\tprint(cls)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ClassRef, 'cls', '__main__#A.c_method.cls'),
		('class A:\n\tdef method(self) -> None:\n\t\tprint(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ThisRef, 'self', '__main__#A.method.self'),
		('a', 'file_input.var', defs.Var, 'a', '__main__#a'),
		('a[0]', 'file_input.getitem', defs.Indexer, '', '__main__#indexer@1'),
		# Primary - Path
		('from a.b.c import A', 'file_input.import_stmt.dotted_name', defs.ImportPath, '', '__main__#import_path@2'),
		('@deco\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', defs.DecoratorPath, '', '__main__#func.decorator_path@4'),
		# Primary - Type
		('a: A.B = 0', 'file_input.anno_assign.typed_getattr', defs.RelayOfType, 'A.B', '__main__#A.B'),
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType, 'int', '__main__#int'),
		('if True:\n\ta: int = 0', 'file_input.if_stmt.if_clause.block.anno_assign.typed_var', defs.VarOfType, 'int', '__main__#if@1.if_clause@2.int'),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType, 'list', '__main__#list'),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType, 'dict', '__main__#dict'),
		('a: Callable[[int], None] = {}', 'file_input.anno_assign.typed_getitem', defs.CallableType, 'Callable', '__main__#Callable'),
		('a: int | str = 0', 'file_input.anno_assign.typed_or_expr', defs.UnionType, 'Union', '__main__#Union'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.typed_none', defs.NullType, 'None', '__main__#func.None'),
		# Primary - FuncCall
		('a(0)', 'file_input.funccall', defs.FuncCall, 'func_call@1', '__main__#func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.funccall', defs.FuncCall, 'func_call@1', '__main__#func_call@1'),
		('a(0)\nfor i in b(): ...', 'file_input.for_stmt.for_in.funccall', defs.FuncCall, 'func_call@16', '__main__#for@11.func_call@16'),
		('super()', 'file_input.funccall', defs.Super, 'super@1', '__main__#super@1'),
		# Primary - Elipsis
		('...', 'file_input.elipsis', defs.Elipsis, '', '__main__#elipsis@1'),
		# Primary - Generator
		('[a for a in []]', 'file_input.list_comp', defs.ListComp, 'list_comp@1', '__main__#list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', defs.DictComp, 'dict_comp@1', '__main__#dict_comp@1'),
		# Literal
		('1', 'file_input.number', defs.Integer, 'int@1', '__main__#int@1'),
		('1.0', 'file_input.number', defs.Float, 'float@1', '__main__#float@1'),
		("'string'", 'file_input.string', defs.String, 'str@1', '__main__#str@1'),
		('True', 'file_input.const_true', defs.Truthy, 'bool@1', '__main__#bool@1'),
		('False', 'file_input.const_false', defs.Falsy, 'bool@1', '__main__#bool@1'),
		('{1: 2}', 'file_input.dict.key_value', defs.Pair, 'Pair@2', '__main__#Pair@2'),
		('[1]', 'file_input.list', defs.List, 'list@1', '__main__#list@1'),
		('{1: 2}', 'file_input.dict', defs.Dict, 'dict@1', '__main__#dict@1'),
		('(1,)', 'file_input.tuple', defs.Tuple, 'tuple@1', '__main__#tuple@1'),
		('None', 'file_input.const_none', defs.Null, 'None', '__main__#None'),
	])
	def test_domain(self, source: str, full_path: str, types: type[T_Node], expected_name: bool, expected_fully: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(type(node), types)
		self.assertEqual(node.domain_name, expected_name)
		self.assertEqual(node.fullyname, expected_fully)

	@data_provider([
		# General
		('...', 'file_input', defs.Entrypoint, '__main__', '__main__'),
		# Statement compound - Block
		('class A: ...', 'file_input.class_def.class_def_raw.block', defs.Block, '__main__#A', '__main__#A'),
		# Statement compound - Flow
		('if True: ...', 'file_input.if_stmt', defs.If, '__main__', '__main__'),
		('if True: ...', 'file_input.if_stmt.if_clause.const_true.', defs.Truthy, '__main__#if@1.if_clause@2', '__main__'),
		('if True: ...\nelif True: ...', 'file_input.if_stmt.elif_clauses.elif_clause.const_true', defs.Truthy, '__main__#if@1.else_if@7', '__main__'),
		('if True: ...\nelse: ...', 'file_input.if_stmt.else_clause.block.elipsis', defs.Elipsis, '__main__#if@1.else@7', '__main__'),
		('while True: ...', 'file_input.while_stmt', defs.While, '__main__', '__main__'),
		('while True: ...', 'file_input.while_stmt.const_true', defs.Truthy, '__main__#while@1', '__main__'),
		('for i in [0]: ...', 'file_input.for_stmt', defs.For, '__main__', '__main__'),
		('for i in [0]: ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar, '__main__#for@1', '__main__'),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt', defs.Try, '__main__', '__main__'),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', defs.Catch, '__main__#try@1', '__main__'),
		('with open(a) as f: ...', 'file_input.with_stmt', defs.With, '__main__', '__main__'),
		('with open(a) as f: ...', 'file_input.with_stmt.with_items.with_item', defs.WithEntry, '__main__#with@1', '__main__'),
		# Statement compound - ClassDef
		('def func() -> None: ...', 'file_input.function_def', defs.Function, '__main__', '__main__'),
		('class A: ...', 'file_input.class_def', defs.Class, '__main__', '__main__'),
		('class E(Enum): ...', 'file_input.class_def', defs.Enum, '__main__', '__main__'),
		('B: TypeAlias = A', 'file_input.class_assign', defs.AltClass, '__main__', '__main__'),
		('T = TypeVar("T")', 'file_input.template_assign', defs.TemplateClass, '__main__', '__main__'),
		# Elements
		('def func(n: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue', defs.Parameter, '__main__#func', '__main__#func'),
		('@deco\ndef func(n: int) -> None: ...', 'file_input.function_def.decorators.decorator', defs.Decorator, '__main__#func', '__main__#func'),
		# Statement simple - Assign
		('a: int = 0', 'file_input.anno_assign', defs.AnnoAssign, '__main__', '__main__'),
		('a = 0', 'file_input.assign', defs.MoveAssign, '__main__', '__main__'),
		('a += 0', 'file_input.aug_assign', defs.AugAssign, '__main__', '__main__'),
		# Statement simple - Other
		('def func() -> int:\n\treturn 0', 'file_input.function_def.function_def_raw.block.return_stmt', defs.Return, '__main__#func', '__main__#func'),
		('raise Exception()', 'file_input.raise_stmt', defs.Throw, '__main__', '__main__'),
		('pass', 'file_input.pass_stmt', defs.Pass, '__main__', '__main__'),
		('break', 'file_input.break_stmt', defs.Break, '__main__', '__main__'),
		('continue', 'file_input.continue_stmt', defs.Continue, '__main__', '__main__'),
		('# abc', 'file_input.comment_stmt', defs.Comment, '__main__', '__main__'),
		('from a.b.c import A', 'file_input.import_stmt', defs.Import, '__main__', '__main__'),
		# Primary - Argument
		('a(0)', 'file_input.funccall.arguments.argvalue', defs.Argument, '__main__', '__main__'),
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue', defs.InheritArgument, '__main__#B', '__main__#B'),
		('a(n=0)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel, '__main__', '__main__'),
		# Primary - Var
		('class A:\n\ta: ClassVar[int] = 0', 'file_input.class_def.class_def_raw.block.class_var_assign.assign_namelist.var', defs.DeclClassVar, '__main__#A', '__main__#A'),
		('class A:\n\ta: int', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclThisVarForward, '__main__#A', '__main__#A'),
		('class A:\n\tdef __init__(self) -> None:\n\t\tself.a: int = 0', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.anno_assign.assign_namelist.getattr', defs.DeclThisVar, '__main__#A.__init__', '__main__#A.__init__'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam, '__main__#A.c_method', '__main__#A.c_method'),
		('class A:\n\tdef method(self) -> None: ...', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam, '__main__#A.method', '__main__#A.method'),
		('a: int = 0', 'file_input.anno_assign.assign_namelist.var', defs.DeclLocalVar, '__main__', '__main__'),
		('if True:\n\ta = 0\nelif True:\n\ta = 1', 'file_input.if_stmt.if_clause.block.assign.assign_namelist.var', defs.DeclLocalVar, '__main__#if@1.if_clause@2', '__main__'),
		('if True:\n\ta = 0\nelif True:\n\ta = 1', 'file_input.if_stmt.elif_clauses.elif_clause.block.assign.assign_namelist.var', defs.DeclLocalVar, '__main__#if@1.else_if@13', '__main__'),
		# Primary - Name
		('class A: ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, '__main__#A', '__main__#A'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.name', defs.TypesName, '__main__#func', '__main__#func'),
		('class E(Enum): ...', 'file_input.class_def.class_def_raw.name', defs.TypesName, '__main__#E', '__main__#E'),
		('B: TypeAlias = A', 'file_input.class_assign.assign_namelist.var', defs.AltTypesName, '__main__#B', '__main__#B'),
		('from a.b.c import A', 'file_input.import_stmt.import_as_names.import_as_name.name', defs.ImportName, '__main__', '__main__'),
		# Primary - Reference
		('a.b', 'file_input.getattr', defs.Relay, '__main__', '__main__'),
		('class A:\n\t@classmethod\n\tdef c_method(cls) -> None:\n\t\tprint(cls)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ClassRef, '__main__#A.c_method', '__main__#A.c_method'),
		('class A:\n\tdef method(self) -> None:\n\t\tprint(self)', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.funccall.arguments.argvalue.var', defs.ThisRef, '__main__#A.method', '__main__#A.method'),
		('a', 'file_input.var', defs.Var, '__main__', '__main__'),
		('a[0]', 'file_input.getitem', defs.Indexer, '__main__', '__main__'),
		# Primary - Path
		('from a.b.c import A', 'file_input.import_stmt.dotted_name', defs.ImportPath, '__main__', '__main__'),
		('@deco\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', defs.DecoratorPath, '__main__#func', '__main__#func'),
		# Primary - Type
		('a: A.B = 0', 'file_input.anno_assign.typed_getattr', defs.RelayOfType, '__main__', '__main__'),
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType, '__main__', '__main__'),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType, '__main__', '__main__'),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType, '__main__', '__main__'),
		('a: Callable[[], None] = {}', 'file_input.anno_assign.typed_getitem', defs.CallableType, '__main__', '__main__'),
		('a: A[B, C] = {}', 'file_input.anno_assign.typed_getitem', defs.CustomType, '__main__', '__main__'),
		('a: A | B = A', 'file_input.anno_assign.typed_or_expr', defs.UnionType, '__main__', '__main__'),
		('a: None = None', 'file_input.anno_assign.typed_none', defs.NullType, '__main__', '__main__'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.typed_none', defs.NullType, '__main__#func', '__main__#func'),
		# Primary - FuncCall
		('a(0)', 'file_input.funccall', defs.FuncCall, '__main__', '__main__'),
		('super()', 'file_input.funccall', defs.Super, '__main__', '__main__'),
		# Primary - Elipsis
		('...', 'file_input.elipsis', defs.Elipsis, '__main__', '__main__'),
		# Primary - Generator
		('[a for a in []]', 'file_input.list_comp', defs.ListComp, '__main__', '__main__'),
		('[a for a in []]', 'file_input.list_comp.comprehension.comp_fors.comp_for.for_namelist.name', defs.DeclLocalVar, '__main__#list_comp@1', '__main__#list_comp@1'),
		('{a: b for a, b in {}}', 'file_input.dict_comp', defs.DictComp, '__main__', '__main__'),
		('{a: b for a, b in {}}', 'file_input.dict_comp.comprehension.comp_fors.comp_for.for_namelist.name[0]', defs.DeclLocalVar, '__main__#dict_comp@1', '__main__#dict_comp@1'),
		# Literal
		('1', 'file_input.number', defs.Integer, '__main__', '__main__'),
	])
	def test_scope_and_namespace(self, source: str, full_path: str, types: type[Node], expected_scope: str, expected_namespace: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(types)
		self.assertEqual(node.scope, expected_scope)
		self.assertEqual(node.namespace, expected_namespace)

	@data_provider([
		('...', 'file_input', ''),
		('class A: ...', 'file_input.class_def.class_def_raw.name', 'A'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', ''),
		('class E(Enum): ...', 'file_input.class_def.class_def_raw.name', 'E'),
		('def func() -> None: ...', 'file_input.function_def.function_def_raw.name', 'func'),
		('if 1: ...', 'file_input.if_stmt.if_clause.block', ''),
		('1', 'file_input.number', '1'),
	])
	def test_tokens(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.tokens, expected)

	@data_provider([
		('class A: ...', 'file_input.class_def', 'entrypoint'),
		('class A: ...', 'file_input.class_def.class_def_raw.block', 'class'),
		('class E(Enum): ...', 'file_input.class_def', 'entrypoint'),
		('def func() -> None: ...', 'file_input.function_def', 'entrypoint'),
		('if 1: ...', 'file_input.if_stmt', 'entrypoint'),
		('1', 'file_input.number', 'entrypoint'),
	])
	def test_parent(self, source: str, full_path: str, expected: str) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.parent.classification, expected)

	@data_provider([
		('...', 'file_input', True),
		('class A: ...', 'file_input.class_def', True),
		('class A: ...', 'file_input.class_def.class_def_raw.block', True),
		('class E(Enum): ...', 'file_input.class_def', True),
		('def func() -> None: ...', 'file_input.function_def', True),
		('if 1: ...', 'file_input.if_stmt', True),
		('1', 'file_input.number', False),
	])
	def test_can_expand(self, source: str, full_path: str, expected: bool) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		self.assertEqual(node.can_expand, expected)

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_var',
			'file_input.class_def.class_def_raw.block.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].number',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].if_clause.const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].if_clause.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].if_clause.const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].if_clause.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
		]),
	])
	def test_procedural_flow(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes_by(full_path)
		all = [in_node.full_path for in_node in node.procedural()]
		try:
			self.assertEqual(all, expected)
		except AssertionError:
			import json
			print(json.dumps(all, indent=2))
			raise

	@data_provider([
		('file_input.class_def', [
			'file_input.class_def.class_def_raw.name',
			'file_input.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.name',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_var',
			'file_input.class_def.class_def_raw.block.class_def.__empty__',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0]',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].assign_namelist.var',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1].number',
			'file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[1]',
			'file_input.class_def.class_def_raw.block.class_def',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].if_clause.const_true',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].if_clause.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[0]',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].if_clause.const_false',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].if_clause.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.block.if_stmt[1]',
			'file_input.class_def.class_def_raw.block.function_def[1]',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.name',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.typedparam.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue.__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.parameters.paramvalue',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.typed_none',
			'file_input.class_def.class_def_raw.block.function_def[2].__empty__',
			'file_input.class_def.class_def_raw.block.function_def[2].function_def_raw.block.elipsis',
			'file_input.class_def.class_def_raw.block.function_def[2]',
		]),
	])
	def test_procedural_ast(self, full_path: str, expected: list[str]) -> None:
		node = self.fixture.shared_nodes_by(full_path)
		all = [in_node.full_path for in_node in node.procedural(order='ast')]
		try:
			self.assertEqual(all, expected)
		except AssertionError:
			import json
			print(json.dumps(all, indent=2))
			raise

	def test_is_a(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(node.is_a(defs.Function), True)
		self.assertEqual(node.is_a(defs.ClassMethod), False)
		self.assertEqual(node.is_a(defs.Method), True)
		self.assertEqual(node.is_a(defs.Class), False)
		self.assertEqual(node.is_a(defs.ClassDef), True)

	def test_as_a(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1]')
		self.assertEqual(defs.Method, type(node))
		self.assertEqual(defs.Method, type(node.as_a(defs.Function)))
		self.assertEqual(defs.Method, type(node.as_a(defs.ClassDef)))

	def test_one_of(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.function_def[1].function_def_raw.parameters.paramvalue.typedparam.__empty__')
		self.assertEqual(defs.Empty, type(node))
		self.assertEqual(defs.Empty, type(node.one_of(defs.Type, defs.Empty)))

	def test_match_feature(self) -> None:
		class NodeA(Node):
			@classmethod
			@override
			def match_feature(cls, via: Node) -> bool:
				return via.tokens == 'a'

		entrypoint = self.fixture.custom_nodes_by('a\nb', 'file_input').as_a(defs.Entrypoint)
		node_a = entrypoint.whole_by('file_input.var[0]')
		node_b = entrypoint.whole_by('file_input.var[1]')
		self.assertEqual(NodeA.match_feature(node_a), True)
		self.assertEqual(NodeA.match_feature(node_b), False)

	def test_dirty_proxify(self) -> None:
		node = self.fixture.shared_nodes_by('file_input.class_def.class_def_raw.block.class_def.class_def_raw.block.assign[0].number')
		proxy = node.dirty_proxify(tokens='10')
		self.assertEqual(isinstance(node, defs.Number), True)
		self.assertEqual(isinstance(proxy, defs.Number), True)
		self.assertEqual(node.tokens, '1')
		self.assertEqual(proxy.tokens, '10')

	@data_provider([
		("""
class A:
	def __init__(self, n: int) -> None:
		self.n: dict[str, int] = {'key': n}
		if True:
			n = 1
			a.b(c, d)
		for key, value in {'a': 1}.items():
			...
""",
			'file_input',
			[
				'<Entrypoint: @0 __main__ (1, 1)..(11, 1)>',
				'+-statements:',
				'  +-<Class: @1 __main__#A (2, 1)..(11, 1)>',
				'    +-symbol: <TypesName: @4 __main__#A.A (2, 7)..(2, 8)>',
				'    +-decorators:',
				'    +-inherits:',
				'    +-template_types:',
				'    +-comment: <Proxy: @2 __main__#A.Empty (0, 0)..(0, 0)>',
				'    +-statements:',
				'      +-<Constructor: @8 __main__#A.__init__ (3, 2)..(11, 1)>',
				'        +-symbol: <TypesName: @11 __main__#A.__init__.__init__ (3, 6)..(3, 14)>',
				'        +-decorators:',
				'        +-parameters:',
				'        | +-<Parameter: @14 __main__#A.__init__.parameter@14 (3, 15)..(3, 19)>',
				'        | | +-symbol: <DeclThisParam: @16 __main__#A.__init__.self (3, 15)..(3, 19)>',
				'        | | +-var_type: <Empty: @18 __main__#A.__init__.Empty (0, 0)..(0, 0)>',
				'        | | +-default_value: <Empty: @19 __main__#A.__init__.Empty (0, 0)..(0, 0)>',
				'        | +-<Parameter: @20 __main__#A.__init__.parameter@20 (3, 21)..(3, 27)>',
				'        |   +-symbol: <DeclParam: @22 __main__#A.__init__.n (3, 21)..(3, 22)>',
				'        |   +-var_type: <VarOfType: @24 __main__#A.__init__.int (3, 24)..(3, 27)>',
				'        |   +-default_value: <Empty: @27 __main__#A.__init__.Empty (0, 0)..(0, 0)>',
				'        +-return_type: <NullType: @30 __main__#A.__init__.None (3, 32)..(3, 36)>',
				'        +-comment: <Proxy: @9 __main__#A.__init__.Empty (0, 0)..(0, 0)>',
				'        +-statements:',
				'          +-<AnnoAssign: @32 __main__#A.__init__.anno_assign@32 (4, 3)..(4, 38)>',
				'          | +-receiver: <DeclThisVar: @34 __main__#A.n (4, 3)..(4, 9)>',
				'          | +-var_type: <DictType: @40 __main__#A.__init__.dict (4, 11)..(4, 25)>',
				'          | | +-type_name: <VarOfType: @41 __main__#A.__init__.dict (4, 11)..(4, 15)>',
				'          | | +-key_type: <VarOfType: @45 __main__#A.__init__.str (4, 16)..(4, 19)>',
				'          | | +-value_type: <VarOfType: @48 __main__#A.__init__.int (4, 21)..(4, 24)>',
				'          | +-value: <Dict: @51 __main__#A.__init__.dict@51 (4, 28)..(4, 38)>',
				'          | | +-items:',
				'          | |   +-<Pair: @52 __main__#A.__init__.Pair@52 (4, 29)..(4, 37)>',
				'          | |     +-first: <String: @53 __main__#A.__init__.str@53 (4, 29)..(4, 34)>',
				'          | |     +-second: <Var: @55 __main__#A.__init__.n (4, 36)..(4, 37)>',
				'          | +-annotation: <Proxy: @-1 __main__#A.__init__.Empty (0, 0)..(0, 0)>',
				'          +-<If: @58 __main__#A.__init__.if@58 (5, 3)..(8, 3)>',
				'          | +-condition: <Truthy: @60 __main__#A.__init__.if@58.if_clause@59.bool@60 (5, 6)..(5, 10)>',
				'          | +-statements:',
				'          | | +-<MoveAssign: @62 __main__#A.__init__.if@58.if_clause@59.move_assign@62 (6, 4)..(6, 9)>',
				'          | | | +-receivers:',
				'          | | | | +-<DeclLocalVar: @64 __main__#A.__init__.if@58.if_clause@59.n (6, 4)..(6, 5)>',
				'          | | | +-value: <Integer: @67 __main__#A.__init__.if@58.if_clause@59.int@67 (6, 8)..(6, 9)>',
				'          | | +-<FuncCall: @69 __main__#A.__init__.if@58.if_clause@59.func_call@69 (7, 4)..(7, 13)>',
				'          | |   +-calls: <Relay: @70 __main__#A.__init__.if@58.if_clause@59.a.b (7, 4)..(7, 7)>',
				'          | |   | +-receiver: <Var: @71 __main__#A.__init__.if@58.if_clause@59.a (7, 4)..(7, 5)>',
				'          | |   +-arguments:',
				'          | |     +-<Argument: @77 __main__#A.__init__.if@58.if_clause@59.argument@77 (7, 8)..(7, 9)>',
				'          | |     | +-label: <Proxy: @-1 __main__#A.__init__.if@58.if_clause@59.Empty (0, 0)..(0, 0)>',
				'          | |     | +-value: <Var: @78 __main__#A.__init__.if@58.if_clause@59.c (7, 8)..(7, 9)>',
				'          | |     +-<Argument: @81 __main__#A.__init__.if@58.if_clause@59.argument@81 (7, 11)..(7, 12)>',
				'          | |       +-label: <Proxy: @-1 __main__#A.__init__.if@58.if_clause@59.Empty (0, 0)..(0, 0)>',
				'          | |       +-value: <Var: @82 __main__#A.__init__.if@58.if_clause@59.d (7, 11)..(7, 12)>',
				'          | +-else_ifs:',
				'          | +-else_clause: <Empty: @88 __main__#A.__init__.if@58.Empty (0, 0)..(0, 0)>',
				'          +-<For: @89 __main__#A.__init__.for@89 (8, 3)..(11, 1)>',
				'            +-symbols:',
				'            | +-<DeclLocalVar: @91 __main__#A.__init__.for@89.key (8, 7)..(8, 10)>',
				'            | +-<DeclLocalVar: @93 __main__#A.__init__.for@89.value (8, 12)..(8, 17)>',
				'            +-for_in: <ForIn: @95 __main__#A.__init__.for@89.for_in@95 (8, 18)..(8, 37)>',
				'            | +-iterates: <FuncCall: @96 __main__#A.__init__.for@89.func_call@96 (8, 21)..(8, 37)>',
				'            |   +-calls: <Relay: @97 __main__#A.__init__.for@89.dict@98.items (8, 21)..(8, 35)>',
				'            |   | +-receiver: <Dict: @98 __main__#A.__init__.for@89.dict@98 (8, 21)..(8, 29)>',
				'            |   |   +-items:',
				'            |   |     +-<Pair: @99 __main__#A.__init__.for@89.Pair@99 (8, 22)..(8, 28)>',
				'            |   |       +-first: <String: @100 __main__#A.__init__.for@89.str@100 (8, 22)..(8, 25)>',
				'            |   |       +-second: <Integer: @102 __main__#A.__init__.for@89.int@102 (8, 27)..(8, 28)>',
				'            |   +-arguments:',
				'            +-statements:',
				'              +-<Elipsis: @108 __main__#A.__init__.for@89.elipsis@108 (9, 4)..(9, 7)>',
			],
	),])
	def test_pretty(self, source: str, full_path: str, expected: list[str]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)

		try:
			self.assertEqual(node.pretty().split('\n'), expected)
		except AssertionError:
			print(node.pretty())
			raise
