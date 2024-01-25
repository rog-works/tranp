from typing import Any
from unittest import TestCase

import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	# General

	@data_provider([
		({
			'statements': [defs.Import, defs.Enum, defs.Class, defs.Class, defs.Function, defs.MoveAssign, defs.AnnoAssign],
			'decl_vars': [defs.MoveAssign, defs.AnnoAssign],
		},),
	])
	def test_entrypoint(self, expected: dict[str, list[type]]) -> None:
		node = self.fixture.shared_nodes.by('file_input').as_a(defs.Entrypoint)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual([type(decl_var) for decl_var in node.decl_vars], expected['decl_vars'])

	# Statement compound

	@data_provider([
		('if True: ...', 'file_input.if_stmt.block', {'statements': [defs.Elipsis], 'decl_vars': []}),
		('if True: a = 0', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign], 'decl_vars': [defs.MoveAssign]}),
		('if True: a += 0', 'file_input.if_stmt.block', {'statements': [defs.AugAssign], 'decl_vars': []}),
	])
	def test_block(self, source: str, full_path: str, expected: dict[str, list[type]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Block)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual([type(decl_var) for decl_var in node.decl_vars_with(defs.DeclBlockVar)], expected['decl_vars'])

	@data_provider([
		('if True:\n\t...\nelif False: ...', 'file_input.if_stmt.elifs.elif_', {'condition': defs.Falsy, 'statements': [defs.Elipsis]}),
	])
	def test_else_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.ElseIf)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('if True:\n\t...\nelif False:\n\t...\nelse: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 1, 'else_statements': [defs.Elipsis]}),
	])
	def test_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.If)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.else_ifs), expected['else_ifs'])
		self.assertEqual([type(statement) for statement in node.else_statements], expected['else_statements'])

	@data_provider([
		('while True: ...', 'file_input.while_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis]}),
	])
	def test_while(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.While)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('for i in range(1): ...', 'file_input.for_stmt', {'symbol': 'i', 'iterates': defs.FuncCall, 'statements': [defs.Elipsis]}),
	])
	def test_for(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.For)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.symbol), defs.DeclLocalVar)
		self.assertEqual(type(node.iterates), expected['iterates'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', {'var_type': 'Exception', 'symbol': 'e', 'statements': [defs.Elipsis]}),
	])
	def test_catch(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Catch)
		self.assertEqual(node.var_type.tokens, expected['var_type'])
		self.assertEqual(type(node.var_type), defs.GeneralType)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.symbol), defs.DeclLocalVar)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 1}),
	])
	def test_try(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Try)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.catches), expected['catches'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[1]', {
			'type': defs.ClassMethod,
			'symbol': 'class_method',
			'access': 'public',
			'decorators': ['classmethod'],
			'parameters': [
				{'symbol': 'cls', 'var_type': 'Empty', 'default_value': 'Empty'},
			],
			'return': defs.GeneralType,
			'decl_vars': [
				{'symbol': 'cls', 'decl_type': defs.Parameter},
				{'symbol': 'lb', 'decl_type': defs.MoveAssign},
			],
			'actual_symbol': None,
			'alias_symbol': None,
			# Belong class only
			'class_symbol': 'Class',
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[2]', {
			'type': defs.Constructor,
			'symbol': '__init__',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
				{'symbol': 'n', 'var_type': 'int', 'default_value': 'Empty'},
				{'symbol': 's', 'var_type': 'str', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 'n', 'decl_type': defs.Parameter},
				{'symbol': 's', 'decl_type': defs.Parameter},
				{'symbol': 'ln', 'decl_type': defs.MoveAssign},
				{'symbol': 'lb', 'decl_type': defs.AnnoAssign},
			],
			'actual_symbol': None,
			'alias_symbol': None,
			# Belong class only
			'class_symbol': 'Class',
			# Constructor only
			'this_vars': ['self.n', 'self.s'],
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.function_def', {
			'type': defs.Closure,
			'symbol': 'method_in_closure',
			'access': 'public',
			'decorators': [],
			'parameters': [],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'i', 'decl_type': defs.For},
			],
			'actual_symbol': None,
			'alias_symbol': None,
			# Closure only
			'binded_this': True,
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[3]', {
			'type': defs.Method,
			'symbol': 'public_method',
			'access': 'public',
			'decorators': ['__alias__'],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
				{'symbol': 'n', 'var_type': 'int', 'default_value': 'Empty'},
			],
			'return': defs.GeneralType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 'n', 'decl_type': defs.Parameter},
				{'symbol': 'e', 'decl_type': defs.Catch},
			],
			'actual_symbol': None,
			'alias_symbol': 'alias',
			# Belong class only
			'class_symbol': 'Class',
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[4]', {
			'type': defs.Method,
			'symbol': '_protected_method',
			'access': 'protected',
			'decorators': [],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
				{'symbol': 's', 'var_type': 'str', 'default_value': 'Empty'},
			],
			'return': defs.ListType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 's', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			'alias_symbol': None,
			# Belong class only
			'class_symbol': 'Class',
		}),
		('file_input.function_def', {
			'type': defs.Function,
			'symbol': 'func',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'b', 'var_type': 'bool', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'b', 'decl_type': defs.Parameter},
				{'symbol': 'lb', 'decl_type': defs.MoveAssign},
			],
			'actual_symbol': None,
			'alias_symbol': None,
		}),
		('file_input.function_def.function_def_raw.block.function_def', {
			'type': defs.Closure,
			'symbol': 'func_in_closure',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'n', 'var_type': 'int', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'n', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			'alias_symbol': None,
			# Closure only
			'binded_this': False,
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Function)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(node.access, expected['access'])
		self.assertEqual([decorator.path.tokens for decorator in node.decorators], expected['decorators'])
		self.assertEqual(len(node.parameters), len(expected['parameters']))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.symbol.tokens, in_expected['symbol'])
			self.assertEqual(parameter.var_type.tokens if not parameter.var_type.is_a(defs.Empty) else 'Empty', in_expected['var_type'])
			self.assertEqual(parameter.default_value.tokens if not parameter.default_value.is_a(defs.Empty) else 'Empty', in_expected['default_value'])

		self.assertEqual(type(node.return_type), expected['return'])
		self.assertEqual(type(node.block), defs.Block)
		self.assertEqual(len(node.decl_vars), len(expected['decl_vars']))
		for index, decl_var in enumerate(node.decl_vars):
			in_expected = expected['decl_vars'][index]
			self.assertEqual(decl_var.symbol.tokens, in_expected['symbol'])
			self.assertEqual(type(decl_var), in_expected['decl_type'])

		self.assertEqual(node.actual_symbol(), expected['actual_symbol'])
		self.assertEqual(node.alias_symbol(), expected['alias_symbol'])

		if isinstance(node, (defs.ClassMethod, defs.Constructor, defs.Method)):
			self.assertEqual(node.class_symbol.tokens, expected['class_symbol'])

		if isinstance(node, defs.Constructor):
			self.assertEqual([var.symbol.tokens for var in node.this_vars if var.is_a(defs.AnnoAssign)], expected['this_vars'])

		if isinstance(node, defs.Closure):
			self.assertEqual(node.binded_this, expected['binded_this'])

	@data_provider([
		('file_input.class_def[3]', {
			'symbol': 'Base',
			'decorators': [],
			'parents': [],
			'constructor_exists': False,
			'class_methods': [],
			'methods': [],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': None,
			'alias_symbol': None,
		}),
		('file_input.class_def[4]', {
			'symbol': 'Class',
			'decorators': ['__alias__'],
			'parents': ['Base'],
			'constructor_exists': True,
			'class_methods': ['class_method'],
			'methods': ['public_method', '_protected_method'],
			'class_vars': ['cn'],
			'this_vars': ['self.n', 'self.s'],
			'actual_symbol': None,
			'alias_symbol': 'Alias',
		}),
		('file_input.class_def[6]', {
			'symbol': 'Actual',
			'decorators': ['__actual__'],
			'parents': [],
			'constructor_exists': False,
			'class_methods': [],
			'methods': [],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': 'Actual',
			'alias_symbol': None,
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Class)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual([decorator.path.tokens for decorator in node.decorators], expected['decorators'])
		self.assertEqual([parent.type_name.tokens for parent in node.parents], expected['parents'])
		self.assertEqual(node.constructor_exists, expected['constructor_exists'])
		self.assertEqual([method.symbol.tokens for method in node.methods], expected['methods'])
		self.assertEqual([var.receiver.tokens for var in node.class_vars], expected['class_vars'])
		self.assertEqual([var.receiver.tokens for var in node.this_vars], expected['this_vars'])
		self.assertEqual(node.actual_symbol(), expected['actual_symbol'])
		self.assertEqual(node.alias_symbol(), expected['alias_symbol'])

	@data_provider([
		('file_input.enum_def', {
			'symbol': 'Values',
			'vars': [
				{'symbol': 'A', 'value': '0'},
				{'symbol': 'B', 'value': '1'},
			],
		}),
	])
	def test_enum(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Enum)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(len(node.vars), len(expected['vars']))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(var.receiver.tokens, in_expected['symbol'])
			self.assertEqual(var.value.tokens, in_expected['value'])
			self.assertEqual(type(var), defs.MoveAssign)

	# Statement simple

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.assign_stmt', {'receiver': 'a', 'var_type': defs.DictType, 'value': defs.Dict}),
	])
	def test_anno_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(type(node.var_type), expected['var_type'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('a[0] += a[1]', 'file_input.assign_stmt', {'receiver': defs.Indexer, 'operator': '+=', 'value': defs.Indexer}),
	])
	def test_aug_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.AugAssign)
		self.assertEqual(type(node.receiver), expected['receiver'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('from a.b.c import A, B', 'file_input.import_stmt', {'import_path': 'a.b.c', 'import_symbols': ['A', 'B']}),
	])
	def test_import(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Import)
		self.assertEqual(node.import_path.tokens, expected['import_path'])
		self.assertEqual(len(node.import_symbols), len(expected['import_symbols']))
		for index, symbol in enumerate(node.import_symbols):
			self.assertEqual(symbol.tokens, expected['import_symbols'][index])

	# Primary

	@data_provider([
		('a', 'file_input.var', defs.Variable),
		('a = 0', 'file_input.assign_stmt.assign.var', defs.DeclLocalVar),
		('a: int = 0', 'file_input.assign_stmt.anno_assign.var', defs.DeclLocalVar),
		('a()', 'file_input.funccall.var', defs.Variable),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.Relay),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr.var', defs.ThisRef),
		('a(b=c)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel),
		('a(b=c)', 'file_input.funccall.arguments.argvalue.var', defs.Variable),
		('a[0]', 'file_input.getitem.var', defs.Variable),
		('a[0].b', 'file_input.getattr', defs.Relay),
		('a[0].b', 'file_input.getattr.getitem.var', defs.Variable),
		('a[0].b', 'file_input.getattr.name', defs.Variable),
		('a.b', 'file_input.getattr', defs.Relay),
		('a.b()', 'file_input.funccall.getattr', defs.Relay),
		('a.b[0]', 'file_input.getitem.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr.getattr.var', defs.Variable),
		('self', 'file_input.var', defs.ThisRef),
		('self.a', 'file_input.getattr', defs.Relay),
		('self.a = self.a', 'file_input.assign_stmt.assign.getattr[0]', defs.Relay),
		('self.a = self.a', 'file_input.assign_stmt.assign.getattr[1]', defs.Relay),
		('self.b: int = self.a', 'file_input.assign_stmt.anno_assign.getattr[0]', defs.DeclThisVar),
		('self.b: int = self.a', 'file_input.assign_stmt.anno_assign.getattr[2]', defs.Relay),
		('self.a()', 'file_input.funccall.getattr', defs.Relay),
		('self.a[0]', 'file_input.getitem.getattr', defs.Relay),
		('self.a.b', 'file_input.getattr', defs.Relay),
		('for a in arr: pass', 'file_input.for_stmt.name', defs.DeclLocalVar),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar),
		('raise e', 'file_input.raise_stmt.var', defs.Variable),
		('raise E() from e', 'file_input.raise_stmt.funccall.var', defs.Variable),
		('raise E() from e', 'file_input.raise_stmt.name', defs.Variable),
		('from path.to import A', 'file_input.import_stmt.import_names.name', defs.ImportName),
		('class B(A): pass', 'file_input.class_def.class_def_raw.name', defs.TypesName),
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.assign_stmt.anno_assign.var[0]', defs.DeclClassVar),
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.assign_stmt.anno_assign.var[2]', defs.Variable),
		('def func(a: int) -> None: pass', 'file_input.function_def.function_def_raw.name', defs.TypesName),
		('def func(a: int) -> None: pass', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclLocalVar),
		('def func(self) -> None: pass', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam),
	])
	def test_fragment(self, source: str, full_path: str, expected: type[defs.Fragment]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Fragment)
		self.assertEqual(type(node), expected)

	@data_provider([
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ThisRef),
		('a(cls.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ClassRef),
		('a[0].b', 'file_input.getattr', defs.Indexer),
		('a.b', 'file_input.getattr', defs.Variable),
		('a.b()', 'file_input.funccall.getattr', defs.Variable),
		('a.b[0]', 'file_input.getitem.getattr', defs.Variable),
		('a.b.c', 'file_input.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr.getattr', defs.Variable),
		('self.a', 'file_input.getattr', defs.ThisRef),
		('self.a()', 'file_input.funccall.getattr', defs.ThisRef),
		('self.a[0]', 'file_input.getitem.getattr', defs.ThisRef),
		('self.a.b', 'file_input.getattr', defs.Relay),
		('self.a().b', 'file_input.getattr', defs.FuncCall),
		('super().b', 'file_input.getattr', defs.Super),
		('"".a', 'file_input.getattr', defs.String),
	])
	def test_relay(self, source: str, full_path: str, expected: type[defs.Reference | defs.FuncCall | defs.Indexer | defs.Literal]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Relay)
		self.assertEqual(type(node.receiver), expected)
		self.assertEqual(type(node.prop), defs.Variable)

	@data_provider([
		('from path.to import A', 'file_input.import_stmt.dotted_name', defs.ImportPath),
		('@path.to(a, b)\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', defs.DecoratorPath),
	])
	def test_path(self, source: str, full_path: str, expected: type[defs.Path]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Path)
		self.assertEqual(type(node), expected)

	@data_provider([
		('a: int = 0', 'file_input.assign_stmt.anno_assign.typed_var', defs.GeneralType),
		('a: list[int] = []', 'file_input.assign_stmt.anno_assign.typed_getitem', defs.ListType),
		('a: list[int] = []', 'file_input.assign_stmt.anno_assign.typed_getitem.typed_var', defs.GeneralType),
		('a: dict[str, int] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem', defs.DictType),
		('a: dict[str, int] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem.typed_slices.typed_var[0]', defs.GeneralType),
		('a: dict[str, int] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem.typed_slices.typed_var[1]', defs.GeneralType),
		('a: str | None = None', 'file_input.assign_stmt.anno_assign.typed_or_expr', defs.UnionType),
		('a: str | None = None', 'file_input.assign_stmt.anno_assign.typed_or_expr.typed_var', defs.GeneralType),
		('a: str | None = None', 'file_input.assign_stmt.anno_assign.typed_or_expr.typed_none', defs.NullType),
		('self.a: int = 0', 'file_input.assign_stmt.anno_assign.typed_var', defs.GeneralType),
		('try: ...\nexcept A.E as e: ...', 'file_input.try_stmt.except_clauses.except_clause.typed_getattr', defs.GeneralType),
		('class B(A): ...', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_var', defs.GeneralType),
		('class B(A[T]): ...', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_getitem', defs.CustomType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_var', defs.GeneralType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.return_type.typed_none', defs.NullType),
		('def func() -> Callable[[], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem', defs.CallableType),
	])
	def test_type(self, source: str, full_path: str, expected: type[defs.Type]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Type)
		self.assertEqual(type(node), expected)

	@data_provider([
		('a: list[int] = []', 'file_input.assign_stmt.anno_assign.typed_getitem', {'value_type': 'int'}),
	])
	def test_list_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.ListType)
		self.assertEqual(node.value_type.tokens, expected['value_type'])

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.assign_stmt.anno_assign.typed_getitem', {'key_type': 'str', 'value_type': 'int'}),
	])
	def test_dict_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.DictType)
		self.assertEqual(node.key_type.tokens, expected['key_type'])
		self.assertEqual(node.value_type.tokens, expected['value_type'])

	@data_provider([
		('def func() -> Callable[[], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem.typed_slices.typed_list', []),
		('def func() -> Callable[[str], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem.typed_slices.typed_list', [defs.GeneralType]),
		('def func() -> Callable[[str, int], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem.typed_slices.typed_list', [defs.GeneralType, defs.GeneralType]),
		('def func() -> Callable[[str, list[int]], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem.typed_slices.typed_list', [defs.GeneralType, defs.ListType]),
		# ('def func() -> Callable[[...], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem.typed_slices.typed_list', [defs.GeneralType, defs.ListType]), XXX Elipsisは一旦非対応
		('def func(f: Callable[[int], None]) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_getitem.typed_slices.typed_list', [defs.GeneralType]),
	])
	def test_type_parameters(self, source: str, full_path: str, expecteds: list[type[defs.Type]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.TypeParameters)
		self.assertEqual(len(node.type_params), len(expecteds))
		for index, in_types in enumerate(node.type_params):
			expected = expecteds[index]
			self.assertEqual(type(in_types), expected)

	@data_provider([
		('a[0]', 'file_input.getitem', {'receiver': 'a', 'key': '0'}),
	])
	def test_indexer(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Indexer)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(node.key.tokens, expected['key'])

	@data_provider([
		('a(b, c)', 'file_input.funccall', {'calls': {'symbol': 'a', 'var_type': defs.Variable}, 'arguments': [{'symbol': 'b', 'var_type': defs.Variable}, {'symbol': 'c', 'var_type': defs.Variable}]}),
	])
	def test_func_call(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.FuncCall)
		self.assertEqual(node.calls.tokens, expected['calls']['symbol'])
		self.assertEqual(type(node.calls), expected['calls']['var_type'])
		self.assertEqual(len(node.arguments), len(expected['arguments']))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.tokens, in_expected['symbol'])
			self.assertEqual(type(argument.value), in_expected['var_type'])

	# Operator

	@data_provider([
		('-1', 'file_input.factor', {'type': defs.Factor, 'operator': '-', 'value': '1'}),
		('+1', 'file_input.factor', {'type': defs.Factor, 'operator': '+', 'value': '1'}),
		('~1', 'file_input.factor', {'type': defs.Factor, 'operator': '~', 'value': '1'}),
		('not 1', 'file_input.not_test', {'type': defs.NotCompare, 'operator': 'not', 'value': '1'}),
	])
	def test_unary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.UnaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(node.value.tokens, expected['value'])

	@data_provider([
		('1 | 2', 'file_input.or_expr', {'type': defs.OrBitwise, 'left': '1', 'operator': '|', 'right': '2'}),
		('1 ^ 2', 'file_input.xor_expr', {'type': defs.XorBitwise, 'left': '1', 'operator': '^', 'right': '2'}),
		('1 & 2', 'file_input.and_expr', {'type': defs.AndBitwise, 'left': '1', 'operator': '&', 'right': '2'}),
		('1 << 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '<<', 'right': '2'}),
		('1 >> 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '>>', 'right': '2'}),
	])
	def test_binary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.BinaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.left.tokens, expected['left'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(node.right.tokens, expected['right'])

	# Literal

	@data_provider([
		('1', 'file_input.number', {'type': defs.Integer, 'value': '1'}),
		('0x1', 'file_input.number', {'type': defs.Integer, 'value': '0x1'}),
		('0.1', 'file_input.number', {'type': defs.Float, 'value': '0.1'}),
	])
	def test_number(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Number)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		("'abcd'", 'file_input.string', {'type': defs.String, 'value': "'abcd'"}),
		('"""abcd\nefgh"""', 'file_input.string', {'type': defs.String, 'value': '"""abcd\nefgh"""'}),
	])
	def test_string(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.String)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		('a = [0, 1]', 'file_input.assign_stmt.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value': '1', 'value_type': defs.Integer}]),
	])
	def test_list(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.List)
		self.assertEqual(len(node.values), len(expected))
		for index, value in enumerate(node.values):
			self.assertEqual(value.tokens, expected[index]['value'])
			self.assertEqual(type(value), expected[index]['value_type'])

	@data_provider([
		('a = {"b": 0, "c": 1}', 'file_input.assign_stmt.assign.dict', [{'key': '"b"', 'value': '0', 'value_type': defs.Integer}, {'key': '"c"', 'value': '1', 'value_type': defs.Integer}]),
	])
	def test_dict(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Dict)
		self.assertEqual(len(node.items), len(expected))
		for index, item in enumerate(node.items):
			self.assertEqual(item.first.tokens, expected[index]['key'])
			self.assertEqual(item.second.tokens, expected[index]['value'])
			self.assertEqual(type(item.second), expected[index]['value_type'])
