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
	_ParamOps = f'file_input.class_def[{_class_begin + 7}]'

	_map = {
		'Values': f'{_Values}',
		'Base': f'{_Base}',
		'Base.__init__': f'{_Base}.class_def_raw.block.function_def[2]',
		'Base.public_method': f'{_Base}.class_def_raw.block.function_def[3]',
		'Class': f'{_Class}',
		'Class.class_method': f'{_Class}.class_def_raw.block.function_def[2]',
		'Class.__init__': f'{_Class}.class_def_raw.block.function_def[3]',
		'Class.__init__.method_in_closure': f'{_Class}.class_def_raw.block.function_def[3].function_def_raw.block.function_def',
		'Class.__init__.method_in_closure.for_in_closure': f'{_Class}.class_def_raw.block.function_def[3].function_def_raw.block.function_def.function_def_raw.block.for_stmt.block.function_def',
		'Class.property_method': f'{_Class}.class_def_raw.block.function_def[4]',
		'Class.public_method': f'{_Class}.class_def_raw.block.function_def[5]',
		'Class._protected_method': f'{_Class}.class_def_raw.block.function_def[6]',
		'func': f'{_func}',
		'func.func_in_closure': f'{_func}.function_def_raw.block.function_def',
		'Class2': f'{_Class2}',
		'GenBase': f'{_GenBase}',
		'GenSub': f'{_GenSub}',
		'ParamOps.star_params': f'{_ParamOps}.class_def_raw.block.function_def[0]',
		'ParamOps.kw_params': f'{_ParamOps}.class_def_raw.block.function_def[1]',
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
				defs.Class,
			],
			'decl_vars': [defs.DeclLocalVar, defs.DeclLocalVar],
		},),
	])
	def test_entrypoint(self, expected: dict[str, list[type]]) -> None:
		node = self.fixture.shared_nodes_by('file_input').as_a(defs.Entrypoint)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual([type(decl_var) for decl_var in node.decl_vars], expected['decl_vars'])

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
		('with open(a) as f:\n\ta = 0', 'file_input.with_stmt.block', {'statements': [defs.MoveAssign]}),
		('def func(a: int) -> None:\n\ta1 = a\n\ta = a1', 'file_input.function_def.function_def_raw.block', {'statements': [defs.MoveAssign, defs.MoveAssign]}),
	])
	def test_block(self, source: str, full_path: str, expected: dict[str, list[type]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Block)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('if True:\n\t...\nelif False: ...', 'file_input.if_stmt.elif_clauses.elif_clause', {'condition': defs.Falsy, 'statements': [defs.Elipsis]}),
	])
	def test_else_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ElseIf)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('if True: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 0, 'else_statements': []}),
		('if True:\n\t...\nelif False:\n\t...\nelif False: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 2, 'else_statements': []}),
		('if True:\n\t...\nelif False:\n\t...\nelse: ...', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis], 'else_ifs': 1, 'else_statements': [defs.Elipsis]}),
	])
	def test_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.If)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.else_ifs), expected['else_ifs'])
		if isinstance(node.else_clause, defs.Else):
			self.assertEqual([type(statement) for statement in node.else_clause.statements], expected['else_statements'])

	@data_provider([
		('while True: ...', 'file_input.while_stmt', {'condition': defs.Truthy, 'statements': [defs.Elipsis]}),
	])
	def test_while(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.While)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('for i in range(1): ...', 'file_input.for_stmt', {'symbols': ['i'], 'iterates': defs.FuncCall, 'statements': [defs.Elipsis]}),
	])
	def test_for(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.For)
		self.assertEqual([symbol.tokens for symbol in node.symbols], expected['symbols'])
		self.assertEqual(len(expected['symbols']), len([symbol for symbol in node.symbols if symbol.is_a(defs.DeclLocalVar)]))
		self.assertEqual(type(node.iterates), expected['iterates'])
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause', {'var_type': 'Exception', 'symbol': 'e', 'statements': [defs.Elipsis]}),
	])
	def test_catch(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Catch)
		self.assertEqual(node.var_type.tokens, expected['var_type'])
		self.assertEqual(defs.VarOfType, type(node.var_type))
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(defs.DeclLocalVar, type(node.symbol))
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])

	@data_provider([
		('try:\n\t...\nexcept Exception as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 1}),
		('try:\n\t...\nexcept ValueError as e:\n\t...\nexcept TypeError as e: ...', 'file_input.try_stmt', {'statements': [defs.Elipsis], 'catches': 2}),
	])
	def test_try(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Try)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.catches), expected['catches'])

	@data_provider([
		('with open(a) as f: ...', 'file_input.with_stmt', {'statements': [defs.Elipsis], 'entries': 1}),
		('with open(a) as f, transaction() as t: ...', 'file_input.with_stmt', {'statements': [defs.Elipsis], 'entries': 2}),
	])
	def test_with(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.With)
		self.assertEqual([type(statement) for statement in node.statements], expected['statements'])
		self.assertEqual(len(node.entries), expected['entries'])

	@data_provider([
		# FIXME Tupleのケースを追加
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
		self.assertEqual(type(node.projection), expected['projection'])
		self.assertEqual(len(expected['fors']), len(node.fors))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual([symbol.tokens for symbol in in_for.symbols], in_expected['symbols'])
			self.assertEqual(type(in_for.iterates), in_expected['iterates'])

		self.assertEqual(type(node.condition), expected['condition'])

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
		self.assertEqual(type(node.projection), expected['projection'])
		self.assertEqual(len(expected['fors']), len(node.fors))
		for index, in_for in enumerate(node.fors):
			in_expected = expected['fors'][index]
			self.assertEqual([symbol.tokens for symbol in in_for.symbols], in_expected['symbols'])
			self.assertEqual(type(in_for.iterates), in_expected['iterates'])

		self.assertEqual(type(node.condition), expected['condition'])

	@data_provider([
		(_ast('Base.__init__'), {
			'type': defs.Constructor,
			'symbol': '__init__',
			'accessor': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'Base',
		}),
		(_ast('Base.public_method'), {
			'type': defs.Method,
			'symbol': 'public_method',
			'accessor': 'public',
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
			'accessor': 'public',
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
			'accessor': 'public',
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
		}),
		(_ast('Class.__init__.method_in_closure'), {
			'type': defs.Closure,
			'symbol': 'method_in_closure',
			'accessor': 'public',
			'decorators': [],
			'parameters': [],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'i', 'decl_type': defs.DeclLocalVar},
			],
			'actual_symbol': None,
		}),
		(_ast('Class.__init__.method_in_closure.for_in_closure'), {
			'type': defs.Closure,
			'symbol': 'for_in_closure',
			'accessor': 'public',
			'decorators': [],
			'parameters': [],
			'return': defs.NullType,
			'decl_vars': [],
			'actual_symbol': None,
		}),
		(_ast('Class.property_method'), {
			'type': defs.Method,
			'symbol': 'property_method',
			'accessor': 'public',
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
			'accessor': 'public',
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
			'accessor': 'protected',
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
			'accessor': 'public',
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
			'accessor': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'n', 'var_type': 'int', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'n', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
		}),
		(_ast('ParamOps.star_params'), {
			'type': defs.Method,
			'symbol': 'star_params',
			'accessor': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
				{'symbol': 'n', 'var_type': 'int', 'default_value': 'Empty'},
				# FIXME list[str]になるように修正。現状は厳密な評価が不要なため対応は保留
				{'symbol': 'args', 'var_type': 'str', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 'n', 'decl_type': defs.Parameter},
				{'symbol': 'args', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'ParamOps',
			# Method only
			'is_property': False,
		}),
		(_ast('ParamOps.kw_params'), {
			'type': defs.Method,
			'symbol': 'kw_params',
			'accessor': 'public',
			'decorators': [],
			'parameters': [
				{'symbol': 'self', 'var_type': 'Empty', 'default_value': 'Empty'},
				{'symbol': 's', 'var_type': 'str', 'default_value': 'Empty'},
				# FIXME list[str]になるように修正。現状は厳密な評価が不要なため対応は保留
				{'symbol': 'args', 'var_type': 'int', 'default_value': 'Empty'},
				# FIXME dict[str, bool]になるように修正。現状は厳密な評価が不要なため対応は保留
				{'symbol': 'kwargs', 'var_type': 'bool', 'default_value': 'Empty'},
			],
			'return': defs.NullType,
			'decl_vars': [
				{'symbol': 'self', 'decl_type': defs.Parameter},
				{'symbol': 's', 'decl_type': defs.Parameter},
				{'symbol': 'args', 'decl_type': defs.Parameter},
				{'symbol': 'kwargs', 'decl_type': defs.Parameter},
			],
			'actual_symbol': None,
			# Belong class only
			'is_abstract': False,
			'class_symbol': 'ParamOps',
			# Method only
			'is_property': False,
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes_by(full_path).as_a(defs.Function)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(node.accessor, expected['accessor'])
		self.assertEqual([decorator.path.tokens for decorator in node.decorators], expected['decorators'])
		self.assertEqual(len(expected['parameters']), len(node.parameters))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.symbol.tokens, in_expected['symbol'])
			self.assertEqual(parameter.var_type.tokens if not parameter.var_type.is_a(defs.Empty) else 'Empty', in_expected['var_type'])
			self.assertEqual(parameter.default_value.tokens if not parameter.default_value.is_a(defs.Empty) else 'Empty', in_expected['default_value'])

		self.assertEqual(type(node.return_type), expected['return'])
		self.assertEqual(defs.Block, type(node.block))
		self.assertEqual(len(expected['decl_vars']), len(node.decl_vars))
		for index, decl_var in enumerate(node.decl_vars):
			in_expected = expected['decl_vars'][index]
			self.assertEqual(type(decl_var), in_expected['decl_type'])
			self.assertEqual(decl_var.symbol.tokens, in_expected['symbol'])

		self.assertEqual(node.actual_symbol, expected['actual_symbol'])

		if isinstance(node, (defs.ClassMethod, defs.Constructor, defs.Method)):
			self.assertEqual(node.is_abstract, expected['is_abstract'])
			self.assertEqual(node.class_types.symbol.tokens, expected['class_symbol'])

		if isinstance(node, defs.Method):
			self.assertEqual(node.is_property, expected['is_property'])

	@data_provider([
		(_ast('Base'), {
			'symbol': 'Base',
			'decorators': [],
			'inherits': [],
			'template_types': [],
			'constructor_exists': True,
			'class_methods': [],
			'methods': ['public_method'],
			'class_vars': [],
			'this_vars': ['self.anno_n', 'self.move_s'],
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
			'this_vars': ['self.move_ns'],
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
			'decorators': [],
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
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual([decorator.path.tokens for decorator in node.decorators], expected['decorators'])
		self.assertEqual([inherit.type_name.tokens for inherit in node.inherits], expected['inherits'])
		self.assertEqual([in_type.type_name.tokens for in_type in node.template_types], expected['template_types'])
		self.assertEqual(node.constructor_exists, expected['constructor_exists'])
		self.assertEqual([method.symbol.tokens for method in node.methods], expected['methods'])
		self.assertEqual([var.tokens for var in node.class_vars], expected['class_vars'])
		self.assertEqual([var.tokens for var in node.this_vars], expected['this_vars'])
		self.assertEqual(node.actual_symbol, expected['actual_symbol'])

	@data_provider([
		('class A(Generic[T]): ...', 'file_input.class_def', {'template_types': [defs.VarOfType]}),
		('class A(Generic[T1, T2]): ...', 'file_input.class_def', {'template_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_class_template_types(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Class)
		self.assertEqual([type(in_type) for in_type in node.template_types], expected['template_types'])

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
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(len(expected['vars']), len(node.vars))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(var.tokens, in_expected['symbol'])
			self.assertEqual(var.declare.as_a(defs.MoveAssign).value.tokens, in_expected['value'])
			self.assertEqual(defs.DeclLocalVar, type(var))
			self.assertEqual(defs.MoveAssign, type(var.declare))
			self.assertEqual(defs.Integer, type(var.declare.as_a(defs.MoveAssign).value))

	@data_provider([
		('A: TypeAlias = int', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.VarOfType}),
		('A: TypeAlias = Literal[0]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.LiteralType}),
		('A: TypeAlias = B.C', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.RelayOfType}),
		('A: TypeAlias = list[str]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.ListType}),
		('A: TypeAlias = dict[str, int]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.DictType}),
		('A: TypeAlias = B[str, int]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.CustomType}),
		('A: TypeAlias = Callable[[str], None]', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.CallableType}),
		('A: TypeAlias = str | None', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.UnionType}),
		('A: TypeAlias = None', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.NullType}),
		('A = TypedDict("A", {"s": str})', 'file_input.class_assign', {'symbol': 'A', 'actual_type': defs.LiteralDictType}),
	])
	def test_alt_class(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AltClass)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(type(node.actual_type), expected['actual_type'])

	@data_provider([
		('A = TypeVar("A")', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVar', 'boundary': defs.Empty, 'covariant': defs.Empty}),
		('A = TypeVar("A", bound=X)', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVar', 'boundary': defs.VarOfType, 'covariant': defs.Empty}),
		('A = TypeVar("A", bound=X.Y)', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVar', 'boundary': defs.RelayOfType, 'covariant': defs.Empty}),
		('A = TypeVar("A", covariant=True)', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVar', 'boundary': defs.Empty, 'covariant': defs.Truthy}),
		('A = TypeVar("A", bound=X, covariant=False)', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVar', 'boundary': defs.VarOfType, 'covariant': defs.Falsy}),
		('A = TypeVarTuple("A")', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'TypeVarTuple', 'boundary': defs.Empty, 'covariant': defs.Empty}),
		('A = ParamSpec("A")', 'file_input.template_assign', {'symbol': 'A', 'definition_type': 'ParamSpec', 'boundary': defs.Empty, 'covariant': defs.Empty}),
	])
	def test_template_class(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.TemplateClass)
		self.assertEqual(node.symbol.tokens, expected['symbol'])
		self.assertEqual(node.definition_type.type_name.tokens, expected['definition_type'])
		self.assertTrue(node.boundary.is_a(expected['boundary']))
		self.assertTrue(node.covariant.is_a(expected['covariant']))

	# Statement simple

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclLocalVar, 'var_type': defs.DictType, 'value': defs.Dict, 'annotation': defs.Empty}),
		('def __init__(self) -> None: self.a: list[str] = []', 'file_input.function_def.function_def_raw.block.anno_assign', {'receiver': 'self.a', 'receiver_type': defs.DeclThisVar, 'var_type': defs.ListType, 'value': defs.List, 'annotation': defs.Empty}),
		('class A: a: ClassVar[str] = ""', 'file_input.class_def.class_def_raw.block.class_var_assign', {'receiver': 'a', 'receiver_type': defs.DeclClassVar, 'var_type': defs.VarOfType, 'value': defs.String, 'annotation': defs.Empty}),
		('class A: a: str', 'file_input.class_def.class_def_raw.block.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclThisVarForward, 'var_type': defs.VarOfType, 'value': defs.Empty, 'annotation': defs.Empty}),
		('class A: a: ClassVar[Literal[0]] = 0', 'file_input.class_def.class_def_raw.block.class_var_assign', {'receiver': 'a', 'receiver_type': defs.DeclClassVar, 'var_type': defs.LiteralType, 'value': defs.Integer, 'annotation': defs.Empty}),
		('class A: a: Literal[0]', 'file_input.class_def.class_def_raw.block.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclThisVarForward, 'var_type': defs.LiteralType, 'value': defs.Empty, 'annotation': defs.Empty}),
		('a: Annotated[dict[str, int], embed("metadata")] = {}', 'file_input.anno_assign', {'receiver': 'a', 'receiver_type': defs.DeclLocalVar, 'var_type': defs.DictType, 'value': defs.Dict, 'annotation': defs.FuncCall}),
	])
	def test_anno_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(type(node.receiver), expected['receiver_type'])
		self.assertEqual(type(node.var_type), expected['var_type'])
		self.assertEqual(type(node.value), expected['value'])
		self.assertTrue(node.var_type.annotation.is_a(expected['annotation']))

	@data_provider([
		('a = {}', 'file_input.assign', {'receivers': ['a'], 'receiver_types': [defs.DeclLocalVar], 'value': defs.Dict, 'var_type': defs.Empty}),
		('a.b = 1', 'file_input.assign', {'receivers': ['a.b'], 'receiver_types': [defs.Relay], 'value': defs.Integer, 'var_type': defs.Empty}),
		('a[0] = []', 'file_input.assign', {'receivers': ['a.0'], 'receiver_types': [defs.Indexer], 'value': defs.List, 'var_type': defs.Empty}),
		('a, b = 1, 2', 'file_input.assign', {'receivers': ['a', 'b'], 'receiver_types': [defs.DeclLocalVar, defs.DeclLocalVar], 'value': defs.Tuple, 'var_type': defs.Empty}),
		('class A:\n\ta: int\n\tdef __init__(self) -> None: self.a = 1', 'file_input.class_def.class_def_raw.block.function_def.function_def_raw.block.assign', {'receivers': ['self.a'], 'receiver_types': [defs.DeclThisVar], 'value': defs.Integer, 'var_type': defs.VarOfType}),
	])
	def test_move_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.MoveAssign)
		self.assertEqual([receiver.tokens for receiver in node.receivers], expected['receivers'])
		self.assertEqual([type(receiver) for receiver in node.receivers], expected['receiver_types'])
		self.assertEqual(type(node.value), expected['value'])
		self.assertTrue(node.var_type.is_a(expected['var_type']))

	@data_provider([
		('a += 1', 'file_input.aug_assign', {'receiver': 'a', 'receiver_type': defs.Var, 'operator': '+=', 'value': defs.Integer}),
		('a.b -= 1.0', 'file_input.aug_assign', {'receiver': 'a.b', 'receiver_type': defs.Relay, 'operator': '-=', 'value': defs.Float}),
		('a[0] *= 0', 'file_input.aug_assign', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'operator': '*=', 'value': defs.Integer}),
	])
	def test_aug_assign(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.AugAssign)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(type(node.receiver), expected['receiver_type'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('del a', 'file_input.del_stmt', {'targets': [defs.Var]}),
		('del a.b', 'file_input.del_stmt', {'targets': [defs.Relay]}),
		('del a[0]', 'file_input.del_stmt', {'targets': [defs.Indexer]}),
		('del a[A], a[B]', 'file_input.del_stmt', {'targets': [defs.Indexer, defs.Indexer]}),
	])
	def test_delete(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Delete)
		self.assertEqual([type(node) for node in node.targets], expected['targets'])

	@data_provider([
		('def func() -> int: return 1', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Integer}),
		('def func() -> None: return', 'file_input.function_def.function_def_raw.block.return_stmt', {'return_value': defs.Empty}),
	])
	def test_return(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Return)
		self.assertEqual(type(node.return_value), expected['return_value'])

	@data_provider([
		('def func() -> Iterator[int]: yield 1', 'file_input.function_def.function_def_raw.block.yield_stmt', {'yield_value': defs.Integer}),
	])
	def test_yield(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Yield)
		self.assertEqual(type(node.yield_value), expected['yield_value'])

	@data_provider([
		('assert True', 'file_input.assert_stmt', {'condition': defs.Truthy, 'assert_body': defs.Empty}),
		('assert n == 1, "message"', 'file_input.assert_stmt', {'condition': defs.Comparison, 'assert_body': defs.String}),
		('assert a.ok, Exception', 'file_input.assert_stmt', {'condition': defs.Relay, 'assert_body': defs.Var}),
	])
	def test_assert(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Assert)
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual(type(node.assert_body), expected['assert_body'])

	@data_provider([
		('raise Exception()', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Empty}),
		('raise Exception() from e', 'file_input.raise_stmt', {'throws': defs.FuncCall, 'via': defs.Var}),
		('raise e', 'file_input.raise_stmt', {'throws': defs.Var, 'via': defs.Empty}),
	])
	def test_throw(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Throw)
		self.assertEqual(type(node.throws), expected['throws'])
		self.assertEqual(type(node.via), expected['via'])

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
		('from a.b.c import A, B as C', 'file_input.import_stmt', {'import_path': 'a.b.c', 'symbols': ['A', 'C']}),
		('from a.b.c import A as B, C', 'file_input.import_stmt', {'import_path': 'a.b.c', 'symbols': ['B', 'C']}),
		('from a.b.c import (A as B, C as D)', 'file_input.import_stmt', {'import_path': 'a.b.c', 'symbols': ['B', 'D']}),
	])
	def test_import(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Import)
		self.assertEqual(node.import_path.tokens, expected['import_path'])
		self.assertEqual([symbol.tokens for symbol in node.symbols], expected['symbols'])

	# Primary

	@data_provider([
		('a(b=c)', 'file_input.funccall.arguments.argvalue.name', defs.ArgumentLabel),
	])
	def test_argument_label(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ArgumentLabel)
		self.assertEqual(type(node), expected)

	@data_provider([
		# Local
		('a = 0', 'file_input.assign.assign_namelist.var', defs.DeclLocalVar),
		('a: int = 0', 'file_input.anno_assign.assign_namelist.var', defs.DeclLocalVar),
		('for i in range(1): ...', 'file_input.for_stmt.for_namelist.name', defs.DeclLocalVar),
		('try: ...\nexcept Exception as e: ...', 'file_input.try_stmt.except_clauses.except_clause.name', defs.DeclLocalVar),
		('class B(A):\n\ta = 0', 'file_input.class_def.class_def_raw.block.assign.assign_namelist.var', defs.DeclLocalVar),  # XXX MoveAssignはクラス変数の宣言にはならない設計
		('lambda a: None', 'file_input.lambdadef.lambdaparams.name', defs.DeclLocalVar),
		('lambda a, b: None', 'file_input.lambdadef.lambdaparams.name[1]', defs.DeclLocalVar),
		# Class/This
		('class B(A):\n\tb: ClassVar[int] = a', 'file_input.class_def.class_def_raw.block.class_var_assign.assign_namelist.var', defs.DeclClassVar),
		('class B(A):\n\tb: int', 'file_input.class_def.class_def_raw.block.anno_assign.assign_namelist.var', defs.DeclThisVarForward),
		('def __init__(self) -> None:\n\tself.b: int = self.a', 'file_input.function_def.function_def_raw.block.anno_assign.assign_namelist.getattr', defs.DeclThisVar),
		# Param/Class/This
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclParam),
		('def func(cls) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclClassParam),
		('def func(self) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.name', defs.DeclThisParam),
		# Name
		('class B(A): ...', 'file_input.class_def.class_def_raw.name', defs.TypesName),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.name', defs.TypesName),
		('A: TypeAlias = int', 'file_input.class_assign.assign_namelist.var', defs.AltTypesName),
		('T = TypeVar("T")', 'file_input.template_assign.assign_namelist.var', defs.AltTypesName),
		('from path.to import A', 'file_input.import_stmt.import_as_names.import_as_name.name', defs.ImportName),
		('from path.to import A as B', 'file_input.import_stmt.import_as_names.import_as_name.name[0]', defs.ImportName),
		('from path.to import A as B', 'file_input.import_stmt.import_as_names.import_as_name.name[1]', defs.ImportName),
		('from path.to import A', 'file_input.import_stmt.import_as_names.import_as_name', defs.ImportAsName),
		('from path.to import A as B', 'file_input.import_stmt.import_as_names.import_as_name', defs.ImportAsName),
	])
	def test_declable(self, source: str, full_path: str, expected: type) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Declable)
		self.assertEqual(type(node), expected)

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
		self.assertEqual(type(node.receiver), expected)
		self.assertEqual(defs.Var, type(node.prop))

	@data_provider([
		('a[0]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['0'], 'key_types': [defs.Integer]}),
		('a[b]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['b'], 'key_types': [defs.Var]}),
		('a[b()]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['b'], 'key_types': [defs.FuncCall]}),
		('a[b.c]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['b.c'], 'key_types': [defs.Relay]}),
		('a[b[0]]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['b.0'], 'key_types': [defs.Indexer]}),
		('a()["b"]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.FuncCall, 'keys': ['"b"'], 'key_types': [defs.String]}),
		('a[0]["b"]', 'file_input.getitem', {'receiver': 'a.0', 'receiver_type': defs.Indexer, 'keys': ['"b"'], 'key_types': [defs.String]}),
		('a[:]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['', '', ''], 'key_types': [defs.Empty]}),
		('a[0:]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['0', '', ''], 'key_types': [defs.Integer, defs.Empty]}),
		('a[0:1]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['0', '1', ''], 'key_types': [defs.Integer, defs.Empty]}),
		('a[1:5:2]', 'file_input.getitem', {'receiver': 'a', 'receiver_type': defs.Var, 'keys': ['1', '5', '2'], 'key_types': [defs.Integer]}),
	])
	def test_indexer(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Indexer)
		self.assertEqual(node.receiver.tokens, expected['receiver'])
		self.assertEqual(type(node.receiver), expected['receiver_type'])
		self.assertEqual([key.tokens for key in node.keys], expected['keys'])
		unexpected_key_types = [key for key in node.keys if type(key) not in expected['key_types']]
		self.assertEqual('ok' if len(unexpected_key_types) == 0 else unexpected_key_types, 'ok')

	@data_provider([
		('from path.to import A', 'file_input.import_stmt.dotted_name', {'type': defs.ImportPath, 'path': 'path.to'}),
		('@path.to(a, b)\ndef func() -> None: ...', 'file_input.function_def.decorators.decorator.dotted_name', {'type': defs.DecoratorPath, 'path': 'path.to'}),
	])
	def test_path(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Path)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['path'])

	@data_provider([
		# General
		('a: int = 0', 'file_input.anno_assign.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: \'int\' = 0', 'file_input.anno_assign.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[0]', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_var[1]', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('self.a: int = 0', 'file_input.anno_assign.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: A.B = ...', 'file_input.anno_assign.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Empty}),
		('a: \'A.B\' = ...', 'file_input.anno_assign.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Empty}),
		('try: ...\nexcept A.E as e: ...', 'file_input.try_stmt.except_clauses.except_clause.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Empty}),
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_var', {'type': defs.VarOfType, 'annotation': defs.Empty}),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Empty}),
		('a: Annotated[int, 0] = 0', 'file_input.anno_assign.typed_var', {'type': defs.VarOfType, 'annotation': defs.Integer}),
		('a: Annotated[\'int\', 0] = 0', 'file_input.anno_assign.typed_var', {'type': defs.VarOfType, 'annotation': defs.Integer}),
		('a: Annotated[A.B, 0] = 0', 'file_input.anno_assign.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Integer}),
		('a: Annotated[\'A.B\', 0] = 0', 'file_input.anno_assign.typed_getattr', {'type': defs.RelayOfType, 'annotation': defs.Integer}),
		('a: Literal[0] = 0', 'file_input.anno_assign.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('a: Literal["a", "b"] = "a"', 'file_input.anno_assign.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('a: list[Literal[0]] = []', 'file_input.anno_assign.typed_getitem.typed_slices.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('a: dict[Literal["a"], int] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('a: dict[str, Literal[0]] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('a: Literal[0] | None = None', 'file_input.anno_assign.typed_or_expr.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('self.a: Literal[0, 1] = 0', 'file_input.anno_assign.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('def func(a: Literal[0]) -> None: ...', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		('def func(a: int) -> Literal[0]: ...', 'file_input.function_def.function_def_raw.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Empty}),
		# ('a: Annotated[Literal[0], 0] = 0', 'file_input.anno_assign.typed_literal', {'type': defs.LiteralType, 'annotation': defs.Integer}), XXX LiteralTypeをAnnotatedで修飾する価値が薄いので非対応
		# Generic - List/Dict/Callable/Custom
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', {'type': defs.ListType, 'annotation': defs.Empty}),
		('a: \'list[int]\' = []', 'file_input.anno_assign.typed_getitem', {'type': defs.ListType, 'annotation': defs.Empty}),
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type': defs.DictType, 'annotation': defs.Empty}),
		('a: \'dict[str, int]\' = {}', 'file_input.anno_assign.typed_getitem', {'type': defs.DictType, 'annotation': defs.Empty}),
		('a: tuple[str, int, bool] = ()', 'file_input.anno_assign.typed_getitem', {'type': defs.CustomType, 'annotation': defs.Empty}),
		('a: \'tuple[str, int, bool]\' = ()', 'file_input.anno_assign.typed_getitem', {'type': defs.CustomType, 'annotation': defs.Empty}),
		('a: Callable[[], None] = ...', 'file_input.anno_assign.typed_getitem', {'type': defs.CallableType, 'annotation': defs.Empty}),
		('a: \'Callable[[], None]\' = ...', 'file_input.anno_assign.typed_getitem', {'type': defs.CallableType, 'annotation': defs.Empty}),
		('def func() -> Callable[[], None]: ...', 'file_input.function_def.function_def_raw.typed_getitem', {'type': defs.CallableType, 'annotation': defs.Empty}),
		('class B(A[T]): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue.typed_getitem', {'type': defs.CustomType, 'annotation': defs.Empty}),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem', {'type': defs.CustomType, 'annotation': defs.Empty}),
		('a: A.B[A.B[A.B], A.B] = {}', 'file_input.anno_assign.typed_getitem.typed_slices.typed_getitem', {'type': defs.CustomType, 'annotation': defs.Empty}),
		('a: Annotated[list[int], "a"] = []', 'file_input.anno_assign.typed_getitem', {'type': defs.ListType, 'annotation': defs.String}),
		('a: Annotated[\'list[int]\', "a"] = []', 'file_input.anno_assign.typed_getitem', {'type': defs.ListType, 'annotation': defs.String}),
		('a: Annotated[dict[str, int], True] = {}', 'file_input.anno_assign.typed_getitem', {'type': defs.DictType, 'annotation': defs.Boolean}),
		('a: Annotated[\'dict[str, int]\', True] = {}', 'file_input.anno_assign.typed_getitem', {'type': defs.DictType, 'annotation': defs.Boolean}),
		('T = TypedDict("T", {"s": int})', 'file_input.class_assign.typed_dict', {'type': defs.LiteralDictType, 'annotation': defs.Empty}),
		# Union
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: A.B | None = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: dict[str, int] | None = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: \'str | None\' = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: \'A.B | None\' = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: \'dict[str, int] | None\' = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Empty}),
		('a: Annotated[str | None, (0, 1)] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Tuple}),
		('a: Annotated[\'str | None\', (0, 1)] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Tuple}),
		('a: Annotated[A.B | None, []] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.List}),
		('a: Annotated[\'A.B | None\', []] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.List}),
		('a: Annotated[dict[str, int] | None, {}] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Dict}),
		('a: Annotated[\'dict[str, int] | None\', {}] = None', 'file_input.anno_assign.typed_or_expr', {'type': defs.UnionType, 'annotation': defs.Dict}),
		# Null
		('a: str | None = None', 'file_input.anno_assign.typed_or_expr.typed_none', {'type': defs.NullType, 'annotation': defs.Empty}),
		('def func(a: int) -> None: ...', 'file_input.function_def.function_def_raw.typed_none', {'type': defs.NullType, 'annotation': defs.Empty}),
	])
	def test_type(self, source: str, full_path: str, expected: dict[str, type[defs.Type]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Type)
		self.assertEqual(type(node), expected['type'])
		self.assertTrue(node.annotation.is_a(expected['annotation']))

	@data_provider([
		('a: list[int] = []', 'file_input.anno_assign.typed_getitem', {'type_name': 'list', 'value_type': defs.VarOfType}),
	])
	def test_list_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.ListType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual(type(node.value_type), expected['value_type'])

	@data_provider([
		('a: dict[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'dict', 'key_type': defs.VarOfType, 'value_type': defs.VarOfType}),
	])
	def test_dict_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.DictType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual(type(node.key_type), expected['key_type'])
		self.assertEqual(type(node.value_type), expected['value_type'])

	@data_provider([
		('a: Callable[[], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [], 'return_type': defs.NullType}),
		('a: Callable[[str], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[str, list[int]], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType, defs.ListType], 'return_type': defs.NullType}),
		('a: Callable[[int], None] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.VarOfType], 'return_type': defs.NullType}),
		('a: Callable[[Literal[0]], Literal[0]] = ...', 'file_input.anno_assign.typed_getitem', {'type_name': 'Callable', 'parameters': [defs.LiteralType], 'return_type': defs.LiteralType}),
		# ('a: Callable[[...], None] = ...', 'file_input.anno_assign.typed_getitem', {}), XXX Elipsisは一旦非対応
	])
	def test_callable_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.CallableType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(parameter) for parameter in node.parameters], expected['parameters'])
		self.assertEqual(type(node.return_type), expected['return_type'])

	@data_provider([
		('a: A[str, int] = {}', 'file_input.anno_assign.typed_getitem', {'type_name': 'A', 'template_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_custom_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.CustomType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(in_type) for in_type in node.template_types], expected['template_types'])

	@data_provider([
		('T = TypedDict("T", {"s": str})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.VarOfType}),
		('T = TypedDict("T", {"d": list[str]})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.ListType}),
		('T = TypedDict("T", {"d": dict[str, int]})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.DictType}),
		('T = TypedDict("T", {"d": Callable[[], None]})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.CallableType}),
		('T = TypedDict("T", {"d": A[str, int, bool]})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.CustomType}),
		('T = TypedDict("T", {"d": str | int})', 'file_input.class_assign.typed_dict', {'type_name': 'dict', 'key_type': defs.LiteralType, 'value_type': defs.UnionType}),
	])
	def test_literal_dict_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.LiteralDictType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual(type(node.key_type), expected['key_type'])
		self.assertEqual(type(node.value_type), expected['value_type'])

	@data_provider([
		('a: str | int = {}', 'file_input.anno_assign.typed_or_expr', {'type_name': 'str.int', 'or_types': [defs.VarOfType, defs.VarOfType]}),
	])
	def test_union_type(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.UnionType)
		self.assertEqual(node.type_name.tokens, expected['type_name'])
		self.assertEqual([type(in_type) for in_type in node.or_types], expected['or_types'])

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
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.calls.tokens, expected['calls']['symbol'])
		self.assertEqual(type(node.calls), expected['calls']['var_type'])
		self.assertEqual(len(expected['arguments']), len(node.arguments))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.tokens, in_expected['symbol'])
			self.assertEqual(type(argument.value), in_expected['var_type'])

	@data_provider([
		('a(a, 1, True)', 'file_input.funccall.arguments.argvalue[1]', {'label': 'Empty', 'value': defs.Integer}),
		('a(1, *a, **b)', 'file_input.funccall.arguments.starargs', {'label': 'Empty', 'value': defs.Var}),
		('a(*[], **c)', 'file_input.funccall.arguments.starargs', {'label': 'Empty', 'value': defs.List}),
		('a(**{})', 'file_input.funccall.arguments.kwargs', {'label': 'Empty', 'value': defs.Dict}),
		('a(*())', 'file_input.funccall.arguments.starargs', {'label': 'Empty', 'value': defs.Tuple}),
		('a(1, **c)', 'file_input.funccall.arguments.kwargs', {'label': 'Empty', 'value': defs.Var}),
		('a(a, label=b, c)', 'file_input.funccall.arguments.argvalue[1]', {'label': 'label', 'value': defs.Var}),
	])
	def test_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Argument)
		self.assertEqual(node.label.tokens if not node.label.is_a(defs.Empty) else 'Empty', expected['label'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('class B(A): ...', 'file_input.class_def.class_def_raw.inherit_arguments.typed_argvalue', {'class_type': defs.VarOfType}),
	])
	def test_inherit_argument(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.InheritArgument)
		self.assertEqual(type(node.class_type), expected['class_type'])

	@data_provider([
		('...', 'file_input.elipsis'),
		('if True: ...', 'file_input.if_stmt.if_clause.block.elipsis'),
		('a = ...', 'file_input.assign.elipsis'),
		('class A: ...', 'file_input.class_def.class_def_raw.block.elipsis'),
	])
	def test_elipsis(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Elipsis, type(self.fixture.custom_nodes_by(source, full_path)))

	@data_provider([
		('lambda: 1', 'file_input.lambdadef', {'symbols': [], 'expression': defs.Integer}),
		('lambda a: None', 'file_input.lambdadef', {'symbols': [defs.DeclLocalVar], 'expression': defs.Null}),
		('lambda a, b: None', 'file_input.lambdadef', {'symbols': [defs.DeclLocalVar, defs.DeclLocalVar], 'expression': defs.Null}),
	])
	def test_lambda(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Lambda)
		self.assertEqual([type(symbol) for symbol in node.symbols], expected['symbols'])
		self.assertEqual(type(node.expression), expected['expression'])

	# Operator

	@data_provider([
		('-1', 'file_input.factor', {'type': defs.Factor, 'operator': '-', 'value': '1'}),
		('+1', 'file_input.factor', {'type': defs.Factor, 'operator': '+', 'value': '1'}),
		('~1', 'file_input.factor', {'type': defs.Factor, 'operator': '~', 'value': '1'}),
		('not 1', 'file_input.not_test', {'type': defs.NotCompare, 'operator': 'not', 'value': '1'}),
	])
	def test_unary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.UnaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(node.value.tokens, expected['value'])

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
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(len(expected['elements']), len(node.elements))
		for index, element in enumerate(node.elements):
			in_expected = expected['elements'][index]
			if type(in_expected) is str:
				self.assertEqual(element.tokens, in_expected)
			else:
				self.assertEqual(type(element), in_expected)

	@data_provider([
		('a if b else c', 'file_input.ternary_test', {'primary': defs.Var, 'condition': defs.Var, 'secondary': defs.Var}),
		('a = 1 if True else 2', 'file_input.assign.ternary_test', {'primary': defs.Integer, 'condition': defs.Truthy, 'secondary': defs.Integer}),
	])
	def test_ternary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.TernaryOperator)
		self.assertEqual(type(node.primary), expected['primary'])
		self.assertEqual(type(node.condition), expected['condition'])
		self.assertEqual(type(node.secondary), expected['secondary'])

	# Literal

	@data_provider([
		('1', 'file_input.number', {'type': defs.Integer, 'value': '1'}),
		('0x1', 'file_input.number', {'type': defs.Integer, 'value': '0x1'}),
		('0.1', 'file_input.number', {'type': defs.Float, 'value': '0.1'}),
	])
	def test_number(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Number)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		("'abcd'", 'file_input.string', {'type': defs.String, 'value': "'abcd'"}),
		('"""abcd\nefgh"""', 'file_input.string', {'type': defs.String, 'value': '"""abcd\nefgh"""'}),
	])
	def test_string(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.String)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

	@data_provider([
		('True', 'file_input.const_true', defs.Truthy),
		('False', 'file_input.const_false', defs.Falsy),
	])
	def test_boolean(self, source: str, full_path: str, expected: type) -> None:
		self.assertEqual(type(self.fixture.custom_nodes_by(source, full_path)), expected)

	@data_provider([
		('a = [0, 1]', 'file_input.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value': '1', 'value_type': defs.Integer}]),
		('a = [0, *[]]', 'file_input.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value_type': defs.List}]),
		('a = [0, *()]', 'file_input.assign.list', [{'value': '0', 'value_type': defs.Integer}, {'value_type': defs.Tuple}]),
	])
	def test_list(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.List)
		self.assertEqual(len(expected), len(node.values))
		for index, value in enumerate(node.values):
			if not isinstance(value, defs.Spread):
				self.assertEqual(value.tokens, expected[index]['value'])
				self.assertEqual(type(value), expected[index]['value_type'])
			else:
				self.assertEqual(type(value.expression), expected[index]['value_type'])

	@data_provider([
		('a = {"b": 0, "c": 1}', 'file_input.assign.dict', [{'key': '"b"', 'value': '0', 'value_type': defs.Integer}, {'key': '"c"', 'value': '1', 'value_type': defs.Integer}]),
		('a = {"b": 0, **{}}', 'file_input.assign.dict', [{'key': '"b"', 'value': '0', 'value_type': defs.Integer}, {'value_type': defs.Dict}]),
	])
	def test_dict(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Dict)
		self.assertEqual(len(expected), len(node.items))
		for index, item in enumerate(node.items):
			if isinstance(item, defs.Pair):
				self.assertEqual(item.first.tokens, expected[index]['key'])
				self.assertEqual(item.second.tokens, expected[index]['value'])
				self.assertEqual(type(item.second), expected[index]['value_type'])
			else:
				self.assertEqual(type(item), expected[index]['value_type'])

	@data_provider([
		('a = ()', 'file_input.assign.tuple', []),
		('a = (1,)', 'file_input.assign.tuple', [{'value': '1', 'value_type': defs.Integer}]),
		('a = (1, "a", (True))', 'file_input.assign.tuple', [{'value': '1', 'value_type': defs.Integer}, {'value': '"a"', 'value_type': defs.String}, {'value': '', 'value_type': defs.Group}]),
		('a = 1, 2', 'file_input.assign.tuple', [{'value': '1', 'value_type': defs.Integer}, {'value': '2', 'value_type': defs.Integer}]),
		('for i in 1, "a": ...', 'file_input.for_stmt.for_in.tuple', [{'value': '1', 'value_type': defs.Integer}, {'value': '"a"', 'value_type': defs.String}]),
		('return 1, True', 'file_input.return_stmt.tuple', [{'value': '1', 'value_type': defs.Integer}, {'value': '', 'value_type': defs.Truthy}]),
		('yield 1,', 'file_input.yield_stmt.tuple', [{'value': '1', 'value_type': defs.Integer}]),
	])
	def test_tuple(self, source: str, full_path: str, expected: list[dict[str, Any]]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path).as_a(defs.Tuple)
		self.assertEqual(len(expected), len(node.values))
		for index, value in enumerate(node.values):
			self.assertEqual(value.tokens, expected[index]['value'])
			self.assertEqual(type(value), expected[index]['value_type'])

	@data_provider([
		('None', 'file_input.const_none'),
	])
	def test_null(self, source: str, full_path: str) -> None:
		self.assertEqual(defs.Null, type(self.fixture.custom_nodes_by(source, full_path)))
