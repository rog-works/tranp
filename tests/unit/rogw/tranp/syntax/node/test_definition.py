from typing import Any
from unittest import TestCase

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


def _ast(before: str) -> str:
	_class_begin = 7
	_T = 'file_input.template_assign'
	_global_n = 'file_input.assign'
	_global_s = 'file_input.anno_assign'
	_Values = f'file_input.class_def[{_class_begin + 0}]'
	_Base = f'file_input.class_def[{_class_begin + 1}]'
	_Class = f'file_input.class_def[{_class_begin + 2}]'
	_func = 'file_input.function_def'
	_Class2 = f'file_input.class_def[{_class_begin + 4}]'
	_GenBase = f'file_input.class_def[{_class_begin + 5}]'
	_GenSub = f'file_input.class_def[{_class_begin + 6}]'

	_map = {
		'Values': f'{_Values}',
		'Base': f'{_Base}',
		'Base.public_method': f'{_Base}.class_def_raw.block.function_def',
		'Class': f'{_Class}',
		'Class.class_method': f'{_Class}.class_def_raw.block.function_def[1]',
		'Class.__init__': f'{_Class}.class_def_raw.block.function_def[2]',
		'Class.__init__.method_in_closure': f'{_Class}.class_def_raw.block.function_def[2].function_def_raw.block.function_def',
		'Class.property_method': f'{_Class}.class_def_raw.block.function_def[3]',
		'Class.public_method': f'{_Class}.class_def_raw.block.function_def[4]',
		'Class._protected_method': f'{_Class}.class_def_raw.block.function_def[5]',
		'func': f'{_func}',
		'func.func_in_closure': f'{_func}.function_def_raw.block.function_def',
		'Class2': f'{_Class2}',
		'GenBase': f'{_GenBase}',
		'GenSub': f'{_GenSub}',
	}
	return _map[before]


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	# General

	@data_provider([
		({
			'statements': [
				defs.Import,
				defs.Import,
				defs.Import,
				defs.Import,
				defs.TemplateClass,
				defs.MoveAssign,
				defs.AnnoAssign,
				defs.Enum,
				defs.Class,
				defs.Class,
				defs.Function,
				defs.Class,
				defs.Class,
				defs.Class,
			],
			'decl_vars': [defs.DeclLocalVar, defs.DeclLocalVar],
		},),
	])
	def test_entrypoint(self, expected: dict[str, list[type]]) -> None:
		node = self.fixture.shared_nodes_by('file_input').as_a(defs.Entrypoint)
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])
		self.assertEqual(expected['decl_vars'], [type(decl_var) for decl_var in node.decl_vars])

	# Statement compound

	@data_provider([
		('if True: ...', 'file_input.if_stmt.if_clause.block', {'statements': [defs.Elipsis]}),
		('if True: a: int = 0', 'file_input.if_stmt.if_clause.block', {'statements': [defs.AnnoAssign]}),
		('if True: a = 0', 'file_input.if_stmt.if_clause.block', {'statements': [defs.MoveAssign]}),
		('if True: a += 0', 'file_input.if_stmt.if_clause.block', {'statements': [defs.AugAssign]}),
		('if True:\n\ta = 0\n\ta = a', 'file_input.if_stmt.if_clause.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
		('if True:\n\ta = 0\n\tb = a', 'file_input.if_stmt.if_clause.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
		('if True:\n\ta = 0\n\tif True: a = 1', 'file_input.if_stmt.if_clause.block', {'statements': [defs.MoveAssign, defs.If]}),
		('if True:\n\ta = 0\n\tfor i in range(1): a = 1', 'file_input.if_stmt.if_clause.block', {'statements': [defs.MoveAssign, defs.For]}),
		('if True:\n\ttry:\n\t\ta = 0\n\texcept Exception as e: ...', 'file_input.if_stmt.if_clause.block', {'statements': [defs.Try]}),
		('try:\n\ta = 0\nexcept Exception as e: ...', 'file_input.try_stmt.try_clause.block', {'statements': [defs.MoveAssign]}),
		('def func(a: int) -> None:\n\ta1 = a\n\ta = a1', 'file_input.function_def.function_def_raw.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
	])
	def test_block(self, source: str, full_path: str, expected: dict[str, list[type]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Block)
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])

	@data_provider([
		('if True:\n\t...\nelif False: ...', 'file_input.if_stmt.elif_clauses.elif_clause', {'condition': defs.Falsy, 'statements': [defs.Elipsis]}),
	])
	def test_else_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ElseIf)
		self.assertEqual(expected['condition'], type(node.condition))
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])

	@data_provider([
		('if True: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 0, 'else_statements': []}),
		('if True:\n\t...\nelif False:\n\t...\nelif False: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 2, 'else_statements': []}),
		('if True:\n\t...\nelif False:\n\t...\nelse: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 1, 'else_statements': [defs.Elipsis]}),
	])
	def test_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.If)
		self.assertEqual(expected['condition'], type(node.condition))
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])
		self.assertEqual(expected['else_ifs'], len(node.else_ifs))
		if isinstance(node.else_clause, defs.Else):
			self.assertEqual(expected['else_statements'], [type(statement) for statement in node.else_clause.statements])

	@data_provider([
		('while True: ...', 'file_input.while_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis]}),
	])
	def test_while(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.While)
		self.assertEqual(expected['condition'], type(node.condition))
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])

	@data_provider([
		('for i in range(1): ...', 'file_input.for_stmt', {'symbols': ['i'], 'iterates': defs.FuncCall, 'statements': [defs.Elipsis]}),
	])
	def test_for(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.For)
		self.assertEqual(expected['symbols'], [symbol.tokens for symbol in node.symbols])
		self.assertEqual(len(expected['symbols']), len([symbol for symbol in node.symbols if symbol.is_a(defs.DeclLocalVar)]))
		self.assertEqual(expected['iterates'], type(node.iterates))
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', {'var_type': 'Exception', 'symbol': 'e', 'statements': [defs.Elipsis]}),
	])
	def test_catch(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Catch)
		self.assertEqual(expected['var_type'], node.var_type.tokens)
		self.assertEqual(defs.VarOfType, type(node.var_type))
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(defs.DeclLocalVar, type(node.symbol))
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 1}),
		('try:\n\t...\nexcept ValueError as e:\n\t...\nexcept TypeError as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 2}),
	])
	def test_try(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Try)
		self.assertEqual(expected['statements'], [type(statement) for statement in node.statements])
		self.assertEqual(expected['catches'], len(node.catches))

	@data_provider([
		('[a for a in {}]', 'file_input.list_comp', {
			'projection': defs.Var,
			'fors': [{'symbols': ['a'], 'iterates': defs.Dict}],
			'condition': defs.Empty,
		}),
		('[a for a in [] if a == 0]', 'file_input.list_comp', {
			'projection': defs.Var,
			'fors': [{'symbols': ['a'], 'iterates': defs.List}],
			'condition': defs.Comparison,
		}),
		('[a for a in [] for b in []]', 'file_input.list_comp', {
			'projection': defs.Var,
			'fors': [{'symbols': ['a'],
			 'iterates': defs.List}, {'symbols': ['b'], 'iterates': defs.List}],
			 'condition': defs.Empty,
		}),
		('[a for a in [b for b in []]]', 'file_input.list_comp', {
			'projection': defs.Var,
			'fors': [{'symbols': ['a'], 'iterates': defs.ListComp}],
			'condition': defs.Empty,
		}),
	])
	def test_list_comp(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ListComp)
		self.assertEqual(expected['projection'], type(node.projection))
		self.assertEqual(len(expected['fors']), len(node.fors))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual(in_expected['symbols'], [symbol.tokens for symbol in in_for.symbols])
			self.assertEqual(in_expected['iterates'], type(in_for.iterates))

		self.assertEqual(expected['condition'], type(node.condition))

	@data_provider([
		('{key: value for key, value in {}.items()}', 'file_input.dict_comp', {
			'projection': defs.Pair,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.FuncCall}],
			'condition': defs.Empty,
		}),
		('{key: value for key, value in {}.items() if a == 0}', 'file_input.dict_comp', {
			'projection': defs.Pair,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.FuncCall}],
			'condition': defs.Comparison,
		}),
		('{key: value for key, value in {}.items() for key2, value2 in {}.items()}', 'file_input.dict_comp', {
			'projection': defs.Pair,
			'fors': [
				{'symbols': ['key', 'value'], 'iterates': defs.FuncCall},
				{'symbols': ['key2', 'value2'], 'iterates': defs.FuncCall},
			],
			'condition': defs.Empty,
		}),
		('{key: value for key, value in {key2: value2 for key2, value2 in {}.items()}}', 'file_input.dict_comp', {
			'projection': defs.Pair,
			'fors': [{'symbols': ['key', 'value'], 'iterates': defs.DictComp}],
			'condition': defs.Empty,
		}),
	])
	def test_dict_comp(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.DictComp)
		self.assertEqual(expected['projection'], type(node.projection))
		self.assertEqual(len(expected['fors']), len(node.fors))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual(in_expected['symbols'], [symbol.tokens for symbol in in_for.symbols])
			self.assertEqual(in_expected['iterates'], type(in_for.iterates))

		self.assertEqual(expected['condition'], type(node.condition))

	@data_provider([
		(_ast('Base.public_method'), {
			'type': defs.Method,
			'symbol': 'public_method',
			'access': 'public',
			'decorators': ['abstractmethod'],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
			],
			'return': defs.VarOfType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			# Belong class only
			'is_abstract': True,
			'class_symbol': 'Base',
			# Method only
			'is_property': False,
		}),
		(_ast('Class.class_method'), {
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
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Class',
		}),
		(_ast('Class.__init__'), {
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
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Class',
			# Constructor only
			'this_vars': ['self.n', 'self.s'],
		}),
		(_ast('Class.__init__.method_in_closure'), {
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
			# Closure only
			'binded_this': True,
		}),
		(_ast('Class.property_method'), {
			'type': defs.Method,
			'symbol': 'property_method',
			'access': 'public',
			'decorators': ['property'],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
			],
			'return': defs.VarOfType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Class',
			# Method only
			'is_property': True,
		}),
		(_ast('Class.public_method'), {
			'type': defs.Method,
			'symbol': 'public_method',
			'access': 'public',
			'decorators': [],
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
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Class',
			# Method only
			'is_property': False,
		}),
		(_ast('Class._protected_method'), {
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
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Class',
			# Method only
			'is_property': False,
		}),
		(_ast('func'), {
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
		}),
		(_ast('func.func_in_closure'), {
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
			# Closure only
			'binded_this': False,
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes_by(full_path).as_a(defs.Function)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(expected['access'], node.access)
		self.assertEqual(expected['decorators'], [decorator.path.tokens for decorator in node.decorators])
		self.assertEqual(len(expected['parameters']), len(node.parameters))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(in_expected['symbol'], parameter.symbol.tokens)
			self.assertEqual(in_expected['var_type'], parameter.var_type.tokens if not parameter.var_type.is_a(defs.Empty) else 'Empty')
			self.assertEqual(in_expected['default_value'], parameter.default_value.tokens if not parameter.default_value.is_a(defs.Empty) else 'Empty')

		self.assertEqual(expected['return'], type(node.return_type))
		self.assertEqual(defs.Block, type(node.block))
		self.assertEqual(len(expected['decl_vars']), len(node.decl_vars))
		for index, decl_var in enumerate(node.decl_vars):
			in_expected = expected['decl_vars'][index]
			self.assertEqual(in_expected['decl_type'], type(decl_var))
			self.assertEqual(in_expected['symbol'], decl_var.symbol.tokens)

		self.assertEqual(expected['actual_symbol'], node.actual_symbol)

		if isinstance(node, (defs.ClassMethod, defs.Constructor, defs.Method)):
			self.assertEqual(expected['is_abstract'], node.is_abstract)
			self.assertEqual(expected['class_symbol'], node.class_types.symbol.tokens)

		if isinstance(node, defs.Constructor):
			self.assertEqual(expected['this_vars'], [this_var.tokens for this_var in node.this_vars])

		if isinstance(node, defs.Method):
			self.assertEqual(expected['is_property'], node.is_property)

		if isinstance(node, defs.Closure):
			self.assertEqual(expected['binded_this'], node.binded_this)

	@data_provider([
		(_ast('Base'), {
			'symbol': 'Base',
			'decorators': [],
			'inherits': [],
			'template_types': [],
			'constructor_exists': False,
			'class_methods': [],
			'methods': ['public_method'],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': None,
		}),
		(_ast('Class'), {
			'symbol': 'Class',
			'decorators': [],
			'inherits': ['Base'],
			'template_types': [],
			'constructor_exists': True,
			'class_methods': ['class_method'],
			'methods': ['property_method', 'public_method', '_protected_method'],
			'class_vars': ['cn'],
			'this_vars': ['self.n', 'self.s'],
			'actual_symbol': None,
		}),
		(_ast('Class2'), {
			'symbol': 'Actual',
			'decorators': ['__actual__'],
			'inherits': [],
			'template_types': [],
			'constructor_exists': False,
			'class_methods': [],
			'methods': [],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': 'Actual',
		}),
		(_ast('GenBase'), {
			'symbol': 'GenBase',
			'decorators': [],
			'inherits': [],
			'template_types': ['T'],
			'constructor_exists': False,
			'class_methods': [],
			'methods': [],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': None,
		}),
		(_ast('GenSub'), {
			'symbol': 'GenSub',
			'decorators': ['__hint_generic__'],
			'inherits': ['GenBase'],
			'template_types': ['T'],
			'constructor_exists': False,
			'class_methods': [],
			'methods': [],
			'class_vars': [],
			'this_vars': [],
			'actual_symbol': None,
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes_by(full_path).as_a(defs.Class)
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(expected['decorators'], [decorator.path.tokens for decorator in node.decorators])
		self.assertEqual(expected['inherits'], [inherit.type_name.tokens for inherit in node.inherits])
		self.assertEqual(expected['template_types'], [in_type.type_name.tokens for in_type in node.template_types])
		self.assertEqual(expected['constructor_exists'], node.constructor_exists)
		self.assertEqual(expected['methods'], [method.symbol.tokens for method in node.methods])
		self.assertEqual(expected['class_vars'], [var.tokens for var in node.class_vars])
		self.assertEqual(expected['this_vars'], [var.tokens for var in node.this_vars])
		self.assertEqual(expected['actual_symbol'], node.actual_symbol)

	@data_provider([
		('class A(Generic[T]): ...', 'file_input.class_def', {'template_types': [defs.VarOfType]}),
		('class A(Generic[T1, T2]): ...', 'file_input.class_def', {'template_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_class_template_types(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Class)
		self.assertEqual(expected['template_types'], [type(in_type) for in_type in node.template_types])

	@data_provider([
		(_ast('Values'), {
			'symbol': 'Values',
			'vars': [
				{'symbol': 'A', 'value': '0'},
				{'symbol': 'B', 'value': '1'},
			],
		}),
	])
	def test_enum(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes_by(full_path).as_a(defs.Enum)
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(len(expected['vars']), len(node.vars))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(in_expected['symbol'], var.tokens)
			self.assertEqual(in_expected['value'], var.declare.as_a(defs.MoveAssign).value.tokens)
			self.assertEqual(defs.DeclLocalVar, type(var))
			self.assertEqual(defs.MoveAssign, type(var.declare))
			self.assertEqual(defs.Integer, type(var.declare.as_a(defs.MoveAssign).value))

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
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AltClass)
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(expected['actual_type'], type(node.actual_type))

	@data_provider([
		('A = TypeVar("A")', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.Empty}),
		('A = TypeVar("A", bound=X)', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.VarOfType}),
		('A = TypeVar("A", bound=X.Y)', 'file_input.template_assign', {'symbol': 'A', 'constraints': defs.RelayOfType}),
	])
	def test_template_class(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.TemplateClass)
		self.assertEqual(expected['symbol'], node.symbol.tokens)
		self.assertEqual(expected['constraints'], type(node.constraints))

	# Statement simple

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclLocalVar, 'var_type': defs.DictType, 'value': defs.Dict}),
		('self.a: list[str] = []', 'file_input.anno_assign', {'receiver': 'self.a', 'receiver_type': defs.DeclThisVar, 'var_type': defs.ListType, 'value': defs.List}),
		('class A: a: str = ""', 'file_input.class_def.class_def_raw.block.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclClassVar, 'var_type': defs.VarOfType, 'value': defs.String}),
	])
	def test_anno_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AnnoAssign)
		self.assertEqual(expected['receiver'], node.receiver.tokens)
		self.assertEqual(expected['receiver_type'], type(node.receiver))
		self.assertEqual(expected['var_type'], type(node.var_type))
		self.assertEqual(expected['value'], type(node.value))

	@data_provider([
		('a = {}', 'file_input.assign', {'receivers': ['a'], 'receiver_types': [defs.DeclLocalVar], 'value': defs.Dict}),
		('a.b = 1', 'file_input.assign', {'receivers': ['a.b'], 'receiver_types': [defs.Relay], 'value': defs.Integer}),
		('a[0] = []', 'file_input.assign', {'receivers': ['a.0'], 'receiver_types': [defs.Indexer], 'value': defs.List}),
	])
	def test_move_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.MoveAssign)
		self.assertEqual(expected['receivers'], [receiver.tokens for receiver in node.receivers])
		self.assertEqual(expected['receiver_types'], [type(receiver) for receiver in node.receivers])
		self.assertEqual(expected['value'], type(node.value))

	@data_provider([
		('a += 1', 'file_input.aug_assign', {'receiver': 'a', 'receiver_type': defs.Var, 'operator': '+=', 'value': defs.Integer}),
		('a.b -= 1.0', 'file_input.aug_assign', {'receiver': 'a.b', 'receiver_type': defs.Relay, 'operator': '-=', 'value': defs.Float}),
		('a[0] *= 0', 'file_input.aug_assign', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'operator': '*=', 'value': defs.Integer}),
	])
	def test_aug_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AugAssign)
		self.assertEqual(expected['receiver'], node.receiver.tokens)
		self.assertEqual(expected['receiver_type'], type(node.receiver))
		self.assertEqual(expected['operator'], node.operator.tokens)
		self.assertEqual(expected['value'], type(node.value))

	@data_provider([
		('def func() -> int: return 1', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Integer}),
		('def func() -> None: return', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Empty}),
	])
	def test_return(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Return)
		self.assertEqual(expected['return_value'], type(node.return_value))

	@data_provider([
		('raise Exception()', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Empty}),
		('raise Exception() from e', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Var}),
		('raise e', 'file_input.raise_stmt', {'throws': defs.Var, 'via': defs.Empty}),
	])
	def test_throw(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Throw)
		self.assertEqual(expected['throws'], type(node.throws))
		self.assertEqual(expected['via'], type(node.via))

	@data_provider([
		('pass', 'file_input.pass_stmt'),
		('if True: pass', 'file_input.if_stmt.if_clause.block.pass_stmt'),
	])
	def test_pass(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Pass, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('break', 'file_input.break_stmt'),
		('for i in range(1): break', 'file_input.for_stmt.block.break_stmt'),
		('while True: break', 'file_input.while_stmt.block.break_stmt'),
	])
	def test_break(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Break, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('continue', 'file_input.continue_stmt'),
		('for i in range(1): continue', 'file_input.for_stmt.block.continue_stmt'),
		('while True: continue', 'file_input.while_stmt.block.continue_stmt'),
	])
	def test_continue(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Continue, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('# abc', 'file_input.comment_stmt'),
		('# abc\na\n# def', 'file_input.comment_stmt[2]'),
		('if True:\n\t# abc\n\t...', 'file_input.if_stmt.if_clause.block.comment_stmt'),
	])
	def test_comment(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Comment, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('from a.b.c import A, B', 'file_input.import_stmt', {'import_path': 'a.b.c', 'symbols': ['A', 'B']}),
		('from a.b.c import (A, B)', 'file_input.import_stmt', {'import_path': 'a.b.c', 'symbols': ['A', 'B']}),
	])
	def test_import(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Import)
		self.assertEqual(expected['import_path'], node.import_path.tokens)
		self.assertEqual(expected['symbols'], [symbol.tokens for symbol in node.symbols])

	# Primary

	@data_provider([
		('a(b=c)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel),
	])
	def test_argument_label(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ArgumentLabel)
		self.assertEqual(expected, type(node))

	@data_provider([
		# Local
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar),
		('a: int = 0', 'file_input.anno_assign.assign_namelist.var', defs.DeclLocalVar),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar),
		('class B(A):\n\ta = 0', 'file_input.class_def.class_def_raw.block.assign.assign_namelist.var', defs.DeclLocalVar),  # XXX MoveAssignはクラス変数の宣言にはならない設計
		# Class/This
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclClassVar),
		('self.b: int = self.a', 'file_input.anno_assign.assign_namelist.getattr', defs.DeclThisVar),
		# Param/Class/This
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclParam),
		('def func(cls) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam),
		('def func(self) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam),
		# Name
		('class B(A): ...', 'file_input.class_def.class_def_raw.name', defs.TypesName),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.name', defs.TypesName),
		('A: TypeAlias = int', 'file_input.class_assign.assign_namelist.var', defs.AltTypesName),
		('T = TypeVar("T")', 'file_input.template_assign.assign_namelist.var', defs.AltTypesName),
		('from path.to import A', 'file_input.import_stmt.import_names.name', defs.ImportName),
	])
	def test_declable(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Declable)
		self.assertEqual(expected, type(node))

	@data_provider([
		# Relay
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
		# Class/This
		('cls', 'file_input.var', defs.ClassRef),
		('a(cls.v)', 'file_input.funccall.arguments.argvalue.getattr.var', defs.ClassRef),
		('self', 'file_input.var', defs.ThisRef),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr.var', defs.ThisRef),
		# Var
		('a', 'file_input.var', defs.Var),
		('a()', 'file_input.funccall.var', defs.Var),
		('a().b', 'file_input.getattr.name', defs.Var),
		('a[0]', 'file_input.getitem.var', defs.Var),
		('a[0].b', 'file_input.getattr.getitem.var', defs.Var),
		('a[0].b', 'file_input.getattr.name', defs.Var),
		('a.b.c', 'file_input.getattr.getattr.var', defs.Var),
		('raise e', 'file_input.raise_stmt.var', defs.Var),
		('raise E() from e', 'file_input.raise_stmt.funccall.var', defs.Var),
		('raise E() from e', 'file_input.raise_stmt.name', defs.Var),
		('a(b=c)', 'file_input.funccall.arguments.argvalue.var', defs.Var),
		('class B(A):\n\tb: int = a', 'file_input.class_def.class_def_raw.block.anno_assign.var', defs.Var),
	])
	def test_reference(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Reference)
		self.assertEqual(expected, type(node))

	@data_provider([
		# left(Reference)
		('a.b.c', 'file_input.getattr', defs.Relay),
		('self.a.b', 'file_input.getattr', defs.Relay),
		('a(cls.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ClassRef),
		('self.a', 'file_input.getattr', defs.ThisRef),
		('self.a()', 'file_input.funccall.getattr', defs.ThisRef),
		('self.a[0]', 'file_input.getitem.getattr', defs.ThisRef),
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', defs.ThisRef),
		('a.b', 'file_input.getattr', defs.Var),
		('a.b()', 'file_input.funccall.getattr', defs.Var),
		('a.b[0]', 'file_input.getitem.getattr', defs.Var),
		('a.b.c', 'file_input.getattr.getattr', defs.Var),
		# left(Indexer)
		('a[0].b', 'file_input.getattr', defs.Indexer),
		# left(FuncCall)
		('self.a().b', 'file_input.getattr', defs.FuncCall),
		('super().b', 'file_input.getattr', defs.Super),
		# left(Literal)
		('"".a', 'file_input.getattr', defs.String),
	])
	def test_relay(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Relay)
		self.assertEqual(expected, type(node.receiver))
		self.assertEqual(defs.Var, type(node.prop))

	@data_provider([
		('a[0]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'key': '0', 'key_type': defs.Integer}),
		('a[b]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'key': 'b', 'key_type': defs.Var}),
		('a[b()]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'key': 'b', 'key_type': defs.FuncCall}),
		('a[b.c]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'key': 'b.c', 'key_type': defs.Relay}),
		('a[b[0]]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'key': 'b.0', 'key_type': defs.Indexer}),
		('a()["b"]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.FuncCall, 'key': '"b"', 'key_type': defs.String}),
		('a[0]["b"]', 'file_input.getitem', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'key': '"b"', 'key_type': defs.String}),
	])
	def test_indexer(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Indexer)
		self.assertEqual(expected['receiver'], node.receiver.tokens)
		self.assertEqual(expected['receiver_type'], type(node.receiver))
		self.assertEqual(expected['key'], node.key.tokens)
		self.assertEqual(expected['key_type'], type(node.key))

	@data_provider([
		('from path.to import A', 'file_input.import_stmt.dotted_name', {'type': defs.ImportPath, 'path': 'path.to'}),
		('@path.to(a, b)\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', {'type': defs.DecoratorPath, 'path': 'path.to'}),
	])
	def test_path(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Path)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['path'], node.tokens)

	@data_provider([
		# General
		('a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem.typed_var', defs.VarOfType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[0]', defs.VarOfType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[1]', defs.VarOfType),
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_var', defs.VarOfType),
		('self.a: int = 0', 'file_input.anno_assign.typed_var', defs.VarOfType),
		('try: ...\nexcept A.E as e: ...', 'file_input.try_stmt.except_clauses.except_clause.typed_getattr', defs.RelayOfType),
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_var', defs.VarOfType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_var', defs.VarOfType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getattr', defs.RelayOfType),
		# Generic - List/Dict/Callable/Custom
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', defs.ListType),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', defs.DictType),
		('def func() -> Callable[[], None]: ...', 'file_input.function_def.function_def_raw.typed_getitem', defs.CallableType),
		('class B(A[T]): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_getitem', defs.CustomType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem', defs.CustomType),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getitem', defs.CustomType),
		# Union
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr', defs.UnionType),
		# Null
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_none', defs.NullType),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.typed_none', defs.NullType),
	])
	def test_type(self, source: str, full_path: str, expected: type[defs.Type]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Type)
		self.assertEqual(expected, type(node))

	@data_provider([
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', {'type_name': 'list', 'value_type': defs.VarOfType}),
	])
	def test_list_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ListType)
		self.assertEqual(expected['type_name'], node.type_name.tokens)
		self.assertEqual(expected['value_type'], type(node.value_type))

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'dict', 'key_type': defs.VarOfType, 'value_type': defs.VarOfType}),
	])
	def test_dict_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.DictType)
		self.assertEqual(expected['type_name'], node.type_name.tokens)
		self.assertEqual(expected['key_type'], type(node.key_type))
		self.assertEqual(expected['value_type'], type(node.value_type))

	@data_provider([
		('a: Callable[[], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [], 'return_type': defs.NullType}),
		('a: Callable[[str], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, list[int]], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.ListType], 'return_type': defs.NullType}),
		('a: Callable[[int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		# ('a: Callable[[...], None] = ...', 'file_input.anno_assign.typed_getitem', {}), XXX Elipsisは一旦非対応
	])
	def test_callable_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.CallableType)
		self.assertEqual(expected['type_name'], node.type_name.tokens)
		self.assertEqual(expected['parameters'], [type(parameter) for parameter in node.parameters])
		self.assertEqual(expected['return_type'], type(node.return_type))

	@data_provider([
		('a: A[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'A', 'template_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_custom_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.CustomType)
		self.assertEqual(expected['type_name'], node.type_name.tokens)
		self.assertEqual(expected['template_types'], [type(in_type) for in_type in node.template_types])

	@data_provider([
		('a: str | int = {}', 'file_input.anno_assign.typed_or_expr', {'type_name': 'str.int', 'or_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_union_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.UnionType)
		self.assertEqual(expected['type_name'], node.type_name.tokens)
		self.assertEqual(expected['or_types'], [type(in_type) for in_type in node.or_types])

	@data_provider([
		('a: None = None', 'file_input.anno_assign.typed_none'),
	])
	def test_null_type(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.NullType, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('a(b, c)', 'file_input.funccall', {
			'type': defs.FuncCall,
			'calls': {'symbol': 'a', 'var_type': defs.Var},
			'arguments': [{'symbol': 'b', 'var_type': defs.Var}, {'symbol': 'c', 'var_type': defs.Var}]
		}),
		('super(b, c)', 'file_input.funccall', {
			'type': defs.Super,
			'calls': {'symbol': 'super', 'var_type': defs.Var},
			'arguments': [{'symbol': 'b', 'var_type': defs.Var}, {'symbol': 'c', 'var_type': defs.Var}]
		}),
	])
	def test_func_call(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.FuncCall)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['calls']['symbol'], node.calls.tokens)
		self.assertEqual(expected['calls']['var_type'], type(node.calls))
		self.assertEqual(len(expected['arguments']), len(node.arguments))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(in_expected['symbol'], argument.value.tokens)
			self.assertEqual(in_expected['var_type'], type(argument.value))

	@data_provider([
		('a(b)', 'file_input.funccall.arguments.argvalue', {'label': 'Empty', 'value': defs.Var}),
		('a(label=b)', 'file_input.funccall.arguments.argvalue', {'label': 'label', 'value': defs.Var}),
	])
	def test_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Argument)
		self.assertEqual(expected['label'], node.label.tokens if not node.label.is_a(defs.Empty) else 'Empty')
		self.assertEqual(expected['value'], type(node.value))

	@data_provider([
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue', {'class_type': defs.VarOfType}),
	])
	def test_inherit_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.InheritArgument)
		self.assertEqual(expected['class_type'], type(node.class_type))

	@data_provider([
		('...', 'file_input.elipsis'),
		('if True: ...', 'file_input.if_stmt.if_clause.block.elipsis'),
		('a = ...', 'file_input.assign.elipsis'),
		('class A: ...', 'file_input.class_def.class_def_raw.block.elipsis'),
	])
	def test_elipsis(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Elipsis, type(self.fixture.custom_nodes_by(source, full_path)))

	# Operator

	@data_provider([
		('-1', 'file_input.factor', {'type': defs.Factor, 'operator': '-', 'value': '1'}),
		('+1', 'file_input.factor', {'type': defs.Factor, 'operator': '+', 'value': '1'}),
		('~1', 'file_input.factor', {'type': defs.Factor, 'operator': '~', 'value': '1'}),
		('not 1', 'file_input.not_test', {'type': defs.NotCompare, 'operator': 'not', 'value': '1'}),
	])
	def test_unary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.UnaryOperator)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['operator'], node.operator.tokens)
		self.assertEqual(expected['value'], node.value.tokens)

	@data_provider([
		('1 or 2', 'file_input.or_test', {'type': defs.OrCompare, 'elements': ['1', 'or', '2']}),
		('1 and 2', 'file_input.and_test', {'type': defs.AndCompare, 'elements': ['1', 'and', '2']}),
		('1 < 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '<', '2']}),
		('1 > 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '>', '2']}),
		('1 == 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '==', '2']}),
		('1 >= 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '>=', '2']}),
		('1 <= 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '<=', '2']}),
		('1 <> 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '<>', '2']}),
		('1 != 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', '!=', '2']}),
		('1 in 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', 'in', '2']}),
		('1 not in 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', 'not.in', '2']}),
		('1 is 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', 'is', '2']}),
		('1 is not 2', 'file_input.comparison', {'type': defs.Comparison, 'elements': ['1', 'is.not', '2']}),
		('1 | 2', 'file_input.or_expr', {'type': defs.OrBitwise, 'elements': ['1', '|', '2']}),
		('1 ^ 2', 'file_input.xor_expr', {'type': defs.XorBitwise, 'elements': ['1', '^', '2']}),
		('1 & 2', 'file_input.and_expr', {'type': defs.AndBitwise, 'elements': ['1', '&', '2']}),
		('1 << 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'elements': ['1', '<<', '2']}),
		('1 >> 2', 'file_input.shift_expr', {'type': defs.ShiftBitwise, 'elements': ['1', '>>', '2']}),
		('1 + 2', 'file_input.sum', {'type': defs.Sum, 'elements': ['1', '+', '2']}),
		('1 - 2', 'file_input.sum', {'type': defs.Sum, 'elements': ['1', '-', '2']}),
		('1 * 2', 'file_input.term', {'type': defs.Term, 'elements': ['1', '*', '2']}),
		('1 / 2', 'file_input.term', {'type': defs.Term, 'elements': ['1', '/', '2']}),
		('1 % 2', 'file_input.term', {'type': defs.Term, 'elements': ['1', '%', '2']}),
		('a + b * c / d - e % f', 'file_input.sum', {'type': defs.Sum, 'elements': ['a', '+', defs.Term, '-', defs.Term]}),
	])
	def test_binary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.BinaryOperator)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(len(expected['elements']), len(node.elements))
		for index, element in enumerate(node.elements):
			in_expected = expected['elements'][index]
			if type(in_expected) is str:
				self.assertEqual(in_expected, element.tokens)
			else:
				self.assertEqual(in_expected, type(element))

	@data_provider([
		('a if b else c', 'file_input.tenary_test', {'primary': defs.Var, 'condition': defs.Var, 'secondary': defs.Var}),
		('a = 1 if True else 2', 'file_input.assign.tenary_test', {'primary': defs.Integer, 'condition': defs.Truthy, 'secondary': defs.Integer}),
	])
	def test_tenary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.TenaryOperator)
		self.assertEqual(expected['primary'], type(node.primary))
		self.assertEqual(expected['condition'], type(node.condition))
		self.assertEqual(expected['secondary'], type(node.secondary))

	# Literal

	@data_provider([
		('1', 'file_input.number', {'type': defs.Integer, 'value': '1'}),
		('0x1', 'file_input.number', {'type': defs.Integer, 'value': '0x1'}),
		('0.1', 'file_input.number', {'type': defs.Float, 'value': '0.1'}),
	])
	def test_number(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Number)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['value'], node.tokens)

	@data_provider([
		("'abcd'", 'file_input.string', {'type': defs.String, 'value': "'abcd'"}),
		('"""abcd\nefgh"""', 'file_input.string', {'type': defs.String, 'value': '"""abcd\nefgh"""'}),
	])
	def test_string(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.String)
		self.assertEqual(expected['type'], type(node))
		self.assertEqual(expected['value'], node.tokens)

	@data_provider([
		('True', 'file_input.const_true', defs.Truthy),
		('False', 'file_input.const_false', defs.Falsy),
	])
	def test_boolean(self, source: str, full_path: str, expected: type) -> None:
		self.assertEqual(expected, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('a = [0, 1]', 'file_input.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value': '1', 'value_type': defs.Integer}]),
	])
	def test_list(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.List)
		self.assertEqual(len(expected), len(node.values))
		for index, value in enumerate(node.values):
			self.assertEqual(expected[index]['value'], value.tokens)
			self.assertEqual(expected[index]['value_type'], type(value))

	@data_provider([
		('a = {"b": 0, "c": 1}', 'file_input.assign.dict', [{'key': '"b"', 'value': '0', 'value_type': defs.Integer}, {'key': '"c"', 'value': '1', 'value_type': defs.Integer}]),
	])
	def test_dict(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Dict)
		self.assertEqual(len(expected), len(node.items))
		for index, item in enumerate(node.items):
			self.assertEqual(expected[index]['key'], item.first.tokens)
			self.assertEqual(expected[index]['value'], item.second.tokens)
			self.assertEqual(expected[index]['value_type'], type(item.second))

	@data_provider([
		('None', 'file_input.const_none'),
	])
	def test_null(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Null, type(self.fixture.custom_nodes_by(source, full_path)))
