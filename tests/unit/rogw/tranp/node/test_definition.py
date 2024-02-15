from typing import Any
from unittest import TestCase

import rogw.tranp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	# General

	@data_provider([
		({
			'statements': [defs.Import, defs.Import, defs.Enum, defs.Class, defs.Class, defs.Function, defs.Class, defs.MoveAssign, defs.AnnoAssign],
			'decl_vars': [defs.DeclLocalVar, defs.DeclLocalVar],
		},),
	])
	def test_entrypoint(self, expected: dict[str, list[type]]) -> None:
		node = self.fixture.shared_nodes.by('file_input').as_a(defs.Entrypoint)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual([type(decl_var) for decl_var in node.decl_vars], expected['decl_vars'])

	# Statement compound

	@data_provider([
		('if True: ...', 'file_input.if_stmt.block', {'statements': [defs.Elipsis]}),
		('if True: a: int = 0', 'file_input.if_stmt.block', {'statements': [defs.AnnoAssign]}),
		('if True: a = 0', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign]}),
		('if True: a += 0', 'file_input.if_stmt.block', {'statements': [defs.AugAssign]}),
		('if True:\n\ta = 0\n\ta = a', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
		('if True:\n\ta = 0\n\tb = a', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
		('if True:\n\ta = 0\n\tif True: a = 1', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign, defs.If]}),
		('if True:\n\ta = 0\n\tfor i in range(1): a = 1', 'file_input.if_stmt.block', {'statements': [defs.MoveAssign, defs.For]}),
		('if True:\n\ttry:\n\t\ta = 0\n\texcept Exception as e: ...', 'file_input.if_stmt.block', {'statements': [defs.Try]}),
		('try:\n\ta = 0\nexcept Exception as e: ...', 'file_input.try_stmt.block', {'statements': [defs.MoveAssign]}),
		('def func(a: int) -> None:\n\ta1 = a\n\ta = a1', 'file_input.function_def.function_def_raw.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
	])
	def test_block(self, source: str, full_path: str, expected: dict[str, list[type]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Block)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('if True:\n\t...\nelif False: ...', 'file_input.if_stmt.elifs.elif_', {'condition': defs.Falsy, 'statements': [defs.Elipsis]}),
	])
	def test_else_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.ElseIf)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('if True: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 0, 'else_statements': []}),
		('if True:\n\t...\nelif False:\n\t...\nelif False: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 2, 'else_statements': []}),
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
		('for i in range(1): ...', 'file_input.for_stmt', {'symbols': ['i'], 'iterates': defs.FuncCall, 'statements': [defs.Elipsis]}),
	])
	def test_for(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.For)
		self.assertEqual([symbol.tokens for symbol in node.symbols], expected['symbols'])
		self.assertEqual(len([symbol for symbol in node.symbols if symbol.is_a(defs.DeclLocalVar)]), len(expected['symbols']))
		self.assertEqual(type(node.iterates), expected['iterates'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', {'var_type': 'Exception', 'symbol': 'e', 'statements': [defs.Elipsis]}),
	])
	def test_catch(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Catch)
		self.assertEqual(node.var_type.tokens, expected['var_type'])
		self.assertEqual(type(node.var_type), defs.VarOfType)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.symbol), defs.DeclLocalVar)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 1}),
		('try:\n\t...\nexcept ValueError as e:\n\t...\nexcept TypeError as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 2}),
	])
	def test_try(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Try)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.catches), expected['catches'])

	@data_provider([
		('[a for a in {}]', 'file_input.list_comp', {
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['a'], 'iterates': defs.Dict}],
			'condition': defs.Empty,
		}),
		('[a for a in [] if a == 0]', 'file_input.list_comp', {
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['a'], 'iterates': defs.List}],
			'condition': defs.Comparison,
		}),
		('[a for a in [] for b in []]', 'file_input.list_comp', {
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['a'],
			 'iterates': defs.List}, {'symbols': ['b'], 'iterates': defs.List}],
			 'condition': defs.Empty,
		}),
		('[a for a in [b for b in []]]', 'file_input.list_comp', {
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['a'], 'iterates': defs.ListComp}],
			'condition': defs.Empty,
		}),
	])
	def test_list_comp(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.ListComp)
		self.assertEqual(type(node.projection_value), expected['projection_value'])
		self.assertEqual(len(node.fors), len(expected['fors']))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual([symbol.tokens for symbol in in_for.symbols], in_expected['symbols'])
			self.assertEqual(type(in_for.iterates), in_expected['iterates'])

		self.assertEqual(type(node.condition), expected['condition'])

	@data_provider([
		('{key: value for key, value in {}.items()}', 'file_input.dict_comp', {
			'projection_key': defs.Variable,
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.FuncCall}],
			'condition': defs.Empty,
		}),
		('{key: value for key, value in {}.items() if a == 0}', 'file_input.dict_comp', {
			'projection_key': defs.Variable,
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.FuncCall}],
			'condition': defs.Comparison,
		}),
		('{key: value for key, value in {}.items() for key2, value2 in {}.items()}', 'file_input.dict_comp', {
			'projection_key': defs.Variable,
			'projection_value': defs.Variable,
			'fors': [
				{'symbols': ['key', 'value'], 'iterates': defs.FuncCall},
				{'symbols': ['key2', 'value2'], 'iterates': defs.FuncCall},
			],
			'condition': defs.Empty,
		}),
		('{key: value for key, value in {key2: value2 for key2, value2 in {}.items()}}', 'file_input.dict_comp', {
			'projection_key': defs.Variable,
			'projection_value': defs.Variable,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.DictComp}],
			'condition': defs.Empty,
		}),
	])
	def test_dict_comp(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.DictComp)
		self.assertEqual(type(node.projection_key), expected['projection_key'])
		self.assertEqual(type(node.projection_value), expected['projection_value'])
		self.assertEqual(len(node.fors), len(expected['fors']))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual([symbol.tokens for symbol in in_for.symbols], in_expected['symbols'])
			self.assertEqual(type(in_for.iterates), in_expected['iterates'])

		self.assertEqual(type(node.condition), expected['condition'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[1]', {
			'type': defs.ClassMethod,
			'symbol': 'class_method',
			'access': 'public',
			'decorators': ['classmethod'],
			'parameters': [
				{'symbol': 'cls', 'var_type': 'Empty', 'default_value': 'Empty'},
			],
			'return': defs.VarOfType,
			'decl_vars': [
				{'symbol': 'cls', 'decl_type': defs.Parameter},
				{'symbol': 'lb', 'decl_type': defs.DeclLocalVar},
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
				{'symbol': 'ln', 'decl_type': defs.DeclLocalVar},
				{'symbol': 'lb', 'decl_type': defs.DeclLocalVar},
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
				{'symbol': 'i', 'decl_type': defs.DeclLocalVar},
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
			'return': defs.VarOfType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 'n', 'decl_type': defs.Parameter},
				{'symbol': 'e', 'decl_type': defs.DeclLocalVar},
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
				{'symbol': 'lb', 'decl_type': defs.DeclLocalVar},
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
			self.assertEqual(type(decl_var), in_expected['decl_type'])
			self.assertEqual(decl_var.symbol.tokens, in_expected['symbol'])

		self.assertEqual(node.actual_symbol, expected['actual_symbol'])
		self.assertEqual(node.alias_symbol, expected['alias_symbol'])

		if isinstance(node, (defs.ClassMethod, defs.Constructor, defs.Method)):
			self.assertEqual(node.class_types.symbol.tokens, expected['class_symbol'])

		if isinstance(node, defs.Constructor):
			self.assertEqual([this_var.tokens for this_var in node.this_vars], expected['this_vars'])

		if isinstance(node, defs.Closure):
			self.assertEqual(node.binded_this, expected['binded_this'])

	@data_provider([
		('file_input.class_def[3]', {
			'symbol': 'Base',
			'decorators': [],
			'inherits': [],
			'generic_types': [],
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
			'inherits': ['Base'],
			'generic_types': [],
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
			'inherits': [],
			'generic_types': [],
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
		self.assertEqual([inherit.type_name.tokens for inherit in node.inherits], expected['inherits'])
		self.assertEqual([in_type.type_name.tokens for in_type in node.generic_types], expected['generic_types'])
		self.assertEqual(node.constructor_exists, expected['constructor_exists'])
		self.assertEqual([method.symbol.tokens for method in node.methods], expected['methods'])
		self.assertEqual([var.tokens for var in node.class_vars], expected['class_vars'])
		self.assertEqual([var.tokens for var in node.this_vars], expected['this_vars'])
		self.assertEqual(node.actual_symbol, expected['actual_symbol'])
		self.assertEqual(node.alias_symbol, expected['alias_symbol'])

	@data_provider([
		('class A(Generic[T]): ...', 'file_input.class_def', {'generic_types': [defs.VarOfType]}),
		('class A(Generic[T1, T2]): ...', 'file_input.class_def', {'generic_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_class_generic_types(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Class)
		self.assertEqual([type(in_type) for in_type in node.generic_types], expected['generic_types'])

	@data_provider([
		('file_input.class_def[2]', {
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
			self.assertEqual(var.tokens, in_expected['symbol'])
			self.assertEqual(var.declare.as_a(defs.MoveAssign).value.tokens, in_expected['value'])
			self.assertEqual(type(var), defs.DeclLocalVar)
			self.assertEqual(type(var.declare), defs.MoveAssign)
			self.assertEqual(type(var.declare.as_a(defs.MoveAssign).value), defs.Integer)

	@data_provider([
		('A: TypeAlias = int', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.VarOfType}),
		('A: TypeAlias = B.C', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.RelayOfType}),
		('A: TypeAlias = list[str]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.ListType}),
		('A: TypeAlias = dict[str, int]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.DictType}),
		('A: TypeAlias = B[str, int]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.CustomType}),
		('A: TypeAlias = Callable[[str], None]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.CallableType}),
		('A: TypeAlias = str | None', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.UnionType}),
		('A: TypeAlias = None', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.NullType}),
	])
	def test_alt_class(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.AltClass)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.actual_type), expected['actual_type'])

	@data_provider([
		('A = TypeVar("A")', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.Empty}),
		('A = TypeVar("A", bound=X)', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.VarOfType}),
		('A = TypeVar("A", bound=X.Y)', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.RelayOfType}),
	])
	def test_template_class(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.TemplateClass)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.constraints), expected['constraints'])

	# Statement simple

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclLocalVar, 'var_type': defs.DictType, 'value': defs.Dict}),
		('self.a: list[str] = []', 'file_input.anno_assign', {'receiver': 'self.a', 'receiver_type': defs.DeclThisVar, 'var_type': defs.ListType, 'value': defs.List}),
		('class A: a: str = ""', 'file_input.class_def.class_def_raw.block.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclClassVar, 'var_type': defs.VarOfType, 'value': defs.String}),
	])
	def test_anno_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.receivers[0].tokens, expected['receiver'])  # XXX Pythonの仕様上AnnoAssignのreceiverは単数のみ
		self.assertEqual(type(node.receivers[0]), expected['receiver_type'])
		self.assertEqual(type(node.var_type), expected['var_type'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('a = {}', 'file_input.assign', {'receivers': ['a'], 'receiver_types': [defs.DeclLocalVar], 'value': defs.Dict}),
		('a.b = 1', 'file_input.assign', {'receivers': ['a.b'], 'receiver_types': [defs.Relay], 'value': defs.Integer}),
		('a[0] = []', 'file_input.assign', {'receivers': ['a.0'], 'receiver_types': [defs.Indexer], 'value': defs.List}),
	])
	def test_move_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.MoveAssign)
		self.assertEqual([receiver.tokens for receiver in node.receivers], expected['receivers'])
		self.assertEqual([type(receiver) for receiver in node.receivers], expected['receiver_types'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('a += 1', 'file_input.aug_assign', {'receiver': 'a', 'receiver_type': defs.Variable, 'operator': '+=', 'value': defs.Integer}),
		('a.b -= 1.0', 'file_input.aug_assign', {'receiver': 'a.b', 'receiver_type': defs.Relay, 'operator': '-=', 'value': defs.Float}),
		('a[0] *= 0', 'file_input.aug_assign', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'operator': '*=', 'value': defs.Integer}),
	])
	def test_aug_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.AugAssign)
		self.assertEqual(node.receivers[0].tokens, expected['receiver'])  # XXX Pythonの仕様上AugAssignのreceiverは単数のみ
		self.assertEqual(type(node.receivers[0]), expected['receiver_type'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('def func() -> int: return 1', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Integer}),
		('def func() -> None: return', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Empty}),
	])
	def test_return(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Return)
		self.assertEqual(type(node.return_value), expected['return_value'])

	@data_provider([
		('raise Exception()', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Empty}),
		('raise Exception() from e', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Variable}),
		('raise e', 'file_input.raise_stmt', {'throws': defs.Variable, 'via': defs.Empty}),
	])
	def test_throw(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Throw)
		self.assertEqual(type(node.throws), expected['throws'])
		self.assertEqual(type(node.via), expected['via'])

	@data_provider([
		('pass', 'file_input.pass_stmt'),
		('if True: pass', 'file_input.if_stmt.block.pass_stmt'),
	])
	def test_pass(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.Pass)

	@data_provider([
		('break', 'file_input.break_stmt'),
		('for i in range(1): break', 'file_input.for_stmt.block.break_stmt'),
		('while True: break', 'file_input.while_stmt.block.break_stmt'),
	])
	def test_break(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.Break)

	@data_provider([
		('continue', 'file_input.continue_stmt'),
		('for i in range(1): continue', 'file_input.for_stmt.block.continue_stmt'),
		('while True: continue', 'file_input.while_stmt.block.continue_stmt'),
	])
	def test_continue(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.Continue)

	@data_provider([
		('from a.b.c import A, B', 'file_input.import_stmt', {'import_path': 'a.b.c', 'import_symbols': ['A', 'B']}),
		('from a.b.c import (A, B)', 'file_input.import_stmt', {'import_path': 'a.b.c', 'import_symbols': ['A', 'B']}),
	])
	def test_import(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Import)
		self.assertEqual(node.import_path.tokens, expected['import_path'])
		self.assertEqual(len(node.import_symbols), len(expected['import_symbols']))
		for index, symbol in enumerate(node.import_symbols):
			self.assertEqual(symbol.tokens, expected['import_symbols'][index])

	# Primary

	@data_provider([
		# Declable - Local
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar),
		('a: int = 0', 'file_input.anno_assign.assign_namelist.var', defs.DeclLocalVar),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclLocalVar),
		('class B(A):\n\ta = 0', 'file_input.class_def.class_def_raw.block.assign.assign_namelist.var', defs.DeclLocalVar),  # XXX MoveAssignはクラス変数の宣言にはならない設計
		# Declable - Class/This
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclClassVar),
		('self.b: int = self.a', 'file_input.anno_assign.assign_namelist.getattr', defs.DeclThisVar),
		# Declable - Param Class/This
		('def func(cls) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam),
		('def func(self) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam),
		# Declable - Name
		('class B(A): ...', 'file_input.class_def.class_def_raw.name', defs.TypesName),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.name', defs.TypesName),
		('from path.to import A', 'file_input.import_stmt.import_names.name', defs.ImportName),
		# Reference - Relay
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.Relay),
		('a().b', 'file_input.getattr', defs.Relay),
		('a[0].b', 'file_input.getattr', defs.Relay),
		('a.b', 'file_input.getattr', defs.Relay),
		('a.b()', 'file_input.funccall.getattr', defs.Relay),
		('a.b[0]', 'file_input.getitem.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr', defs.Relay),
		('a.b.c', 'file_input.getattr.getattr', defs.Relay),
		('self.a', 'file_input.getattr', defs.Relay),
		('self.a = self.a', 'file_input.assign.assign_namelist.getattr', defs.Relay),
		('self.a = self.a', 'file_input.assign.getattr', defs.Relay),
		('self.b: int = self.a', 'file_input.anno_assign.getattr', defs.Relay),
		('self.a()', 'file_input.funccall.getattr', defs.Relay),
		('self.a.b', 'file_input.getattr', defs.Relay),
		('self.a[0]', 'file_input.getitem.getattr', defs.Relay),
		# Reference - Class/This
		('cls', 'file_input.var', defs.ClassRef),
		('a(cls.v)', 'file_input.funccall.arguments.argvalue.getattr.var', defs.ClassRef),
		('self', 'file_input.var', defs.ThisRef),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr.var', defs.ThisRef),
		# Reference - Label
		('a(b=c)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel),
		# Reference - Variable
		('a', 'file_input.var', defs.Variable),
		('a()', 'file_input.funccall.var', defs.Variable),
		('a().b', 'file_input.getattr.name', defs.Variable),
		('a[0]', 'file_input.getitem.var', defs.Variable),
		('a[0].b', 'file_input.getattr.getitem.var', defs.Variable),
		('a[0].b', 'file_input.getattr.name', defs.Variable),
		('a.b.c', 'file_input.getattr.getattr.var', defs.Variable),
		('raise e', 'file_input.raise_stmt.var', defs.Variable),
		('raise E() from e', 'file_input.raise_stmt.funccall.var', defs.Variable),
		('raise E() from e', 'file_input.raise_stmt.name', defs.Variable),
		('a(b=c)', 'file_input.funccall.arguments.argvalue.var', defs.Variable),
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.anno_assign.var', defs.Variable),
	])
	def test_fragment(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Fragment)
		self.assertEqual(type(node), expected)

	@data_provider([
		# left(Reference)
		('a.b.c', 'file_input.getattr', defs.Relay),
		('self.a.b', 'file_input.getattr', defs.Relay),
		('a(cls.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ClassRef),
		('self.a', 'file_input.getattr', defs.ThisRef),
		('self.a()', 'file_input.funccall.getattr', defs.ThisRef),
		('self.a[0]', 'file_input.getitem.getattr', defs.ThisRef),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ThisRef),
		('a.b', 'file_input.getattr', defs.Variable),
		('a.b()', 'file_input.funccall.getattr', defs.Variable),
		('a.b[0]', 'file_input.getitem.getattr', defs.Variable),
		('a.b.c', 'file_input.getattr.getattr', defs.Variable),
		# left(Indexer)
		('a[0].b', 'file_input.getattr', defs.Indexer),
		# left(FuncCall)
		('self.a().b', 'file_input.getattr', defs.FuncCall),
		('super().b', 'file_input.getattr', defs.Super),
		# left(Literal)
		('"".a', 'file_input.getattr', defs.String),
	])
	def test_relay(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Relay)
		self.assertEqual(type(node.receiver), expected)
		self.assertEqual(type(node.prop), defs.Variable)

	@data_provider([
		('from path.to import A', 'file_input.import_stmt.dotted_name', {'type': defs.ImportPath, 'path': 'path.to'}),
		('@path.to(a, b)\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', {'type': defs.DecoratorPath, 'path': 'path.to'}),
	])
	def test_path(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Path)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['path'])

	@data_provider([
		('a[0]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Variable, 'key': '0', 'key_type': defs.Integer}),
		('a[b]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Variable, 'key': 'b', 'key_type': defs.Variable}),
		('a[b()]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Variable, 'key': 'b', 'key_type': defs.FuncCall}),
		('a[b.c]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Variable, 'key': 'b.c', 'key_type': defs.Relay}),
		('a[b[0]]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Variable, 'key': 'b.0', 'key_type': defs.Indexer}),
		('a()["b"]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.FuncCall, 'key': '"b"', 'key_type': defs.String}),
		('a[0]["b"]', 'file_input.getitem', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'key': '"b"', 'key_type': defs.String}),
	])
	def test_indexer(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Indexer)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(type(node.receiver), expected['receiver_type'])
		self.assertEqual(node.key.tokens, expected['key'])
		self.assertEqual(type(node.key), expected['key_type'])

	@data_provider([
		# General
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem.typed_var', defs.VarOfType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[0]', defs.VarOfType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[1]', defs.VarOfType),
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_var', defs.VarOfType),
		('self.a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType),
		('try: ...\nexcept A.E as e: ...', 'file_input.try_stmt.except_clauses.except_clause.typed_getattr', defs.RelayOfType),
		('class B(A): ...', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_var', defs.VarOfType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_var', defs.VarOfType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getattr', defs.RelayOfType),
		# Generic - List/Dict/Callable/Custom
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType),
		('def func() -> Callable[[], None]: ...', 'file_input.function_def.function_def_raw.return_type.typed_getitem', defs.CallableType),
		('class B(A[T]): ...', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_getitem', defs.CustomType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem', defs.CustomType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getitem', defs.CustomType),
		# Union
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr', defs.UnionType),
		# Null
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_none', defs.NullType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.return_type.typed_none', defs.NullType),
	])
	def test_type(self, source: str, full_path: str, expected: type[defs.Type]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Type)
		self.assertEqual(type(node), expected)

	@data_provider([
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', {'type_name': 'list', 'value_type': defs.VarOfType}),
	])
	def test_list_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.ListType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual(type(node.value_type), expected['value_type'])

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'dict', 'key_type': defs.VarOfType, 'value_type': defs.VarOfType}),
	])
	def test_dict_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.DictType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual(type(node.key_type), expected['key_type'])
		self.assertEqual(type(node.value_type), expected['value_type'])

	@data_provider([
		('a: Callable[[], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [], 'return_type': defs.NullType}),
		('a: Callable[[str], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, list[int]], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.ListType], 'return_type': defs.NullType}),
		('a: Callable[[int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		# ('a: Callable[[...], None] = ...', 'file_input.anno_assign.typed_getitem', {}), XXX Elipsisは一旦非対応
	])
	def test_callable_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.CallableType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(parameter) for parameter in node.parameters], expected['parameters'])
		self.assertEqual(type(node.return_type), expected['return_type'])

	@data_provider([
		('a: A[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'A', 'template_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_custom_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.CustomType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(in_type) for in_type in node.template_types], expected['template_types'])

	@data_provider([
		('a: str | int = {}', 'file_input.anno_assign.typed_or_expr', {'type_name': 'str.int', 'or_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_union_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.UnionType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(in_type) for in_type in node.or_types], expected['or_types'])

	@data_provider([
		('a: None = None', 'file_input.anno_assign.typed_none'),
	])
	def test_null_type(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.NullType)

	@data_provider([
		('a(b, c)', 'file_input.funccall', {
			'type': defs.FuncCall,
			'calls': {'symbol': 'a', 'var_type': defs.Variable},
			'arguments': [{'symbol': 'b', 'var_type': defs.Variable}, {'symbol': 'c', 'var_type': defs.Variable}]
		}),
		('super(b, c)', 'file_input.funccall', {
			'type': defs.Super,
			'calls': {'symbol': 'super', 'var_type': defs.Variable},
			'arguments': [{'symbol': 'b', 'var_type': defs.Variable}, {'symbol': 'c', 'var_type': defs.Variable}]
		}),
	])
	def test_func_call(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.FuncCall)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.calls.tokens, expected['calls']['symbol'])
		self.assertEqual(type(node.calls), expected['calls']['var_type'])
		self.assertEqual(len(node.arguments), len(expected['arguments']))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.tokens, in_expected['symbol'])
			self.assertEqual(type(argument.value), in_expected['var_type'])

	@data_provider([
		('a(b)', 'file_input.funccall.arguments.argvalue', {'label': 'Empty', 'value': defs.Variable}),
		('a(label=b)', 'file_input.funccall.arguments.argvalue', {'label': 'label', 'value': defs.Variable}),
	])
	def test_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Argument)
		self.assertEqual(node.label.tokens if not node.label.is_a(defs.Empty) else 'Empty', expected['label'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('class B(A): ...', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue', {'class_type': defs.VarOfType}),
	])
	def test_inherit_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.InheritArgument)
		self.assertEqual(type(node.class_type), expected['class_type'])

	@data_provider([
		('...', 'file_input.elipsis'),
		('if True: ...', 'file_input.if_stmt.block.elipsis'),
		('a = ...', 'file_input.assign.elipsis'),
		('class A: ...', 'file_input.class_def.class_def_raw.block.elipsis'),
	])
	def test_elipsis(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.Elipsis)

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
		('1 or 2', 'file_input.or_test', {'type': defs.OrCompare, 'left': '1', 'operator': 'or', 'right': ['2']}),
		('1 and 2', 'file_input.and_test', {'type': defs.AndCompare, 'left': '1', 'operator': 'and', 'right': ['2']}),
		('1 < 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '<', 'right': ['2']}),
		('1 > 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '>', 'right': ['2']}),
		('1 == 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '==', 'right': ['2']}),
		('1 >= 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '>=', 'right': ['2']}),
		('1 <= 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '<=', 'right': ['2']}),
		('1 <> 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '<>', 'right': ['2']}),
		('1 != 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': '!=', 'right': ['2']}),
		('1 in 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': 'in', 'right': ['2']}),
		('1 not in 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': 'not.in', 'right': ['2']}),
		('1 is 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': 'is', 'right': ['2']}),
		('1 is not 2', 'file_input.comparison', {'type': defs.Comparison, 'left': '1', 'operator': 'is.not', 'right': ['2']}),
		('1 | 2', 'file_input.or_expr', {'type': defs.OrBitwise, 'left': '1', 'operator': '|', 'right': ['2']}),
		('1 ^ 2', 'file_input.xor_expr', {'type': defs.XorBitwise, 'left': '1', 'operator': '^', 'right': ['2']}),
		('1 & 2', 'file_input.and_expr', {'type': defs.AndBitwise, 'left': '1', 'operator': '&', 'right': ['2']}),
		('1 << 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '<<', 'right': ['2']}),
		('1 >> 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'left': '1', 'operator': '>>', 'right': ['2']}),
		('1 + 2', 'file_input.sum', {'type': defs.Sum, 'left': '1', 'operator': '+', 'right': ['2']}),
		('1 - 2', 'file_input.sum', {'type': defs.Sum, 'left': '1', 'operator': '-', 'right': ['2']}),
		('1 * 2', 'file_input.term', {'type': defs.Term, 'left': '1', 'operator': '*', 'right': ['2']}),
		('1 / 2', 'file_input.term', {'type': defs.Term, 'left': '1', 'operator': '/', 'right': ['2']}),
		('1 % 2', 'file_input.term', {'type': defs.Term, 'left': '1', 'operator': '%', 'right': ['2']}),
	])
	def test_binary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.BinaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.left.tokens, expected['left'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual([r.tokens for r in node.right], expected['right'])

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
		('True', 'file_input.const_true', defs.Truthy),
		('False', 'file_input.const_false', defs.Falsy),
	])
	def test_boolean(self, source: str, full_path: str, expected: type) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), expected)

	@data_provider([
		('a = [0, 1]', 'file_input.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value': '1', 'value_type': defs.Integer}]),
	])
	def test_list(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.List)
		self.assertEqual(len(node.values), len(expected))
		for index, value in enumerate(node.values):
			self.assertEqual(value.tokens, expected[index]['value'])
			self.assertEqual(type(value), expected[index]['value_type'])

	@data_provider([
		('a = {"b": 0, "c": 1}', 'file_input.assign.dict', [{'key': '"b"', 'value': '0', 'value_type': defs.Integer}, {'key': '"c"', 'value': '1', 'value_type': defs.Integer}]),
	])
	def test_dict(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Dict)
		self.assertEqual(len(node.items), len(expected))
		for index, item in enumerate(node.items):
			self.assertEqual(item.first.tokens, expected[index]['key'])
			self.assertEqual(item.second.tokens, expected[index]['value'])
			self.assertEqual(type(item.second), expected[index]['value_type'])

	@data_provider([
		('None', 'file_input.const_none'),
	])
	def test_null(self, source: str, full_path: str) -> None:
		self.assertEqual(type(self.fixture.custom_nodes(source).by(full_path)), defs.Null)
