from typing import Any
from unittest import TestCase

import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	# Statement compound

	@data_provider([
		('if True:\n\tpass', 'file_input.if_stmt', {'condition': defs.Truthy, 'statements': [defs.Pass]}),
	])
	def test_if(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.If)
		self.assertEqual(type(node.condition), expected['condition'])
		for index, statement in enumerate(node.statements):
			in_expected = expected['statements'][index]
			self.assertEqual(type(statement), in_expected)

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[1]', {
			'type': defs.Method,
			'name': 'func1',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'value', 'type': 'int', 'default': 'Empty'},
			],
			'return': defs.GeneralType,
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[2]', {
			'type': defs.Method,
			'name': '_func2',
			'access': 'protected',
			'decorators': [
				{'symbol': 'deco_func', 'arguments': [{'value': "'hoge'"}]},
			],
			'parameters': [
				{'name': 'self', 'type': 'Empty', 'default': 'Empty'},
				{'name': 'text', 'type': 'str', 'default': 'Empty'},
			],
			'return': defs.ListType,
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[3].function_def_raw.block.function_def', {
			'type': defs.Closure,
			'name': 'closure',
			'access': 'public',
			'decorators': [],
			'parameters': [],
			'return': defs.NullType,
		}),
		('file_input.class_def[4].class_def_raw.block.function_def[4]', {
			'type': defs.ClassMethod,
			'name': 'cls_func',
			'access': 'public',
			'decorators': [
				{'symbol': 'classmethod', 'arguments': []},
			],
			'parameters': [
				{'name': 'cls', 'type': 'Empty', 'default': 'Empty'},
			],
			'return': defs.GeneralType,
		}),
		('file_input.function_def', {
			'type': defs.Function,
			'name': 'func3',
			'access': 'public',
			'decorators': [],
			'parameters': [
				{'name': 'ok', 'type': 'bool', 'default': 'Empty'},
			],
			'return': defs.NullType,
		}),
	])
	def test_function(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Function)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(node.access, expected['access'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.path.tokens, in_expected['symbol'])
			self.assertEqual(len(decorator.arguments), len(in_expected['arguments']))
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.tokens, in_arg_expected['value'])

		self.assertEqual(len(node.parameters), len(expected['parameters']))
		for index, parameter in enumerate(node.parameters):
			in_expected = expected['parameters'][index]
			self.assertEqual(parameter.symbol.tokens, in_expected['name'])
			self.assertEqual(parameter.var_type.tokens if not parameter.var_type.is_a(defs.Empty) else 'Empty', in_expected['type'])
			self.assertEqual(parameter.default_value.tokens if not parameter.default_value.is_a(defs.Empty) else 'Empty', in_expected['default'])

		self.assertEqual(type(node.return_type), expected['return'])
		self.assertEqual(type(node.block), defs.Block)

	@data_provider([
		('file_input.class_def[3]', {
			'name': 'Base',
			'decorators': [],
			'parents': [],
			'constructor': {},
			'methods': [],
			'this_vars': [],
		}),
		('file_input.class_def[4]', {
			'name': 'Hoge',
			'decorators': [
				{'symbol': 'deco', 'arguments': [{'value': 'A'}, {'value': 'A.B'}]},
			],
			'parents': [
				{'symbol': 'Base'},
			],
			'constructor': {
				'decl_vars': [
					{'symbol': 'self', 'type': 'Empty'},
					{'symbol': 'v', 'type': 'int'},
					{'symbol': 's', 'type': 'str'},
				],
			},
			'methods': [
				{'name': 'func1'},
				{'name': '_func2'},
			],
			'this_vars': [
				{'symbol': 'self.v', 'type': defs.AnnoAssign},
				{'symbol': 'self.s', 'type': defs.AnnoAssign},
			],
		}),
	])
	def test_class(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Class)
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(len(node.decorators), len(expected['decorators']))
		for index, decorator in enumerate(node.decorators):
			in_expected = expected['decorators'][index]
			self.assertEqual(decorator.path.tokens, in_expected['symbol'])
			for index_arg, argument in enumerate(decorator.arguments):
				in_arg_expected = in_expected['arguments'][index_arg]
				self.assertEqual(argument.value.tokens, in_arg_expected['value'])

		self.assertEqual(len(node.parents), len(expected['parents']))
		for index, parent in enumerate(node.parents):
			in_expected = expected['parents'][index]
			self.assertEqual(parent.tokens, in_expected['symbol'])

		self.assertEqual(node.constructor_exists, len(expected['constructor'].keys()) > 0)
		if node.constructor_exists:
			in_expected = expected['constructor']
			constructor = node.constructor
			self.assertEqual(type(constructor), defs.Constructor)
			self.assertEqual(len(constructor.decl_vars), len(in_expected['decl_vars']))
			for index, var in enumerate(constructor.decl_vars):
				in_var_expected = in_expected['decl_vars'][index]
				if isinstance(var, defs.AnnoAssign):
					self.assertEqual(var.receiver.tokens, in_var_expected['symbol'])
					self.assertEqual(var.var_type.tokens, in_var_expected['type'])
				elif isinstance(var, defs.MoveAssign):
					self.assertEqual(var.receiver.tokens, in_var_expected['symbol'])
					self.assertEqual('Empty', in_var_expected['type'])
				elif isinstance(var, defs.Parameter):
					self.assertEqual(var.symbol.tokens, in_var_expected['symbol'])
					self.assertEqual(var.var_type.tokens if not var.var_type.is_a(defs.Empty) else 'Empty', in_var_expected['type'])

		self.assertEqual(len(node.methods), len(expected['methods']))
		for index, method in enumerate(node.methods):
			in_expected = expected['methods'][index]
			self.assertEqual(type(method), defs.Method)
			self.assertEqual(method.symbol.tokens, in_expected['name'])

		self.assertEqual(len(node.this_vars), len(expected['this_vars']))
		for index, var in enumerate(node.this_vars):
			in_expected = expected['this_vars'][index]
			self.assertEqual(type(var), in_expected['type'])
			self.assertEqual(var.receiver.tokens, in_expected['symbol'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.enum_def', {
			'name': 'Values',
			'vars': [
				{'symbol': 'A', 'value': '0'},
				{'symbol': 'B', 'value': '1'},
			],
		}),
	])
	def test_enum(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Enum)
		self.assertEqual(node.symbol.tokens, expected['name'])
		self.assertEqual(len(node.vars), len(expected['vars']))
		for index, var in enumerate(node.vars):
			in_expected = expected['vars'][index]
			self.assertEqual(var.receiver.tokens, in_expected['symbol'])
			self.assertEqual(var.value.tokens, in_expected['value'])

	# Statement simple

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0]', {
			'symbol': 'map',
			'var_type': defs.DictType,
			'value': defs.Dict,
		}),
	])
	def test_anno_assign(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.AnnoAssign)
		self.assertEqual(node.receiver.tokens, expected['symbol'])
		self.assertEqual(type(node.var_type), expected['var_type'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[5]', {
			'symbol': defs.Indexer,
			'operator': '+=',
			'value': defs.Indexer,
		}),
	])
	def test_aug_assign(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.AugAssign)
		self.assertEqual(type(node.receiver), expected['symbol'])
		self.assertEqual(node.operator.tokens, expected['operator'])
		self.assertEqual(type(node.value), expected['value'])

	@data_provider([
		('file_input.import_stmt[1]', {
			'module_path': 'py2cpp.compatible.cpp.enum',
			'import_symbols': [
				{'symbol': 'CEnum'},
				{'symbol': 'A'},
			],
		}),
	])
	def test_import(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Import)
		self.assertEqual(node.import_path.tokens, expected['module_path'])
		self.assertEqual(len(node.import_symbols), len(expected['import_symbols']))
		for index, symbol in enumerate(node.import_symbols):
			in_expected = expected['import_symbols'][index]
			self.assertEqual(symbol.tokens, in_expected['symbol'])

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
		('a(self.v)', 'file_input.funccall.arguments.argvalue.getattr', {'receiver': defs.ThisRef, 'property': defs.Variable}),
		('a[0].b', 'file_input.getattr', {'receiver': defs.Indexer, 'property': defs.Variable}),
		('a.b', 'file_input.getattr', {'receiver': defs.Variable, 'property': defs.Variable}),
		('a.b()', 'file_input.funccall.getattr', {'receiver': defs.Variable, 'property': defs.Variable}),
		('a.b[0]', 'file_input.getitem.getattr', {'receiver': defs.Variable, 'property': defs.Variable}),
		('a.b.c', 'file_input.getattr', {'receiver': defs.Relay, 'property': defs.Variable}),
		('a.b.c', 'file_input.getattr.getattr', {'receiver': defs.Variable, 'property': defs.Variable}),
		('self.a', 'file_input.getattr', {'receiver': defs.ThisRef, 'property': defs.Variable}),
		('self.a()', 'file_input.funccall.getattr', {'receiver': defs.ThisRef, 'property': defs.Variable}),
		('self.a[0]', 'file_input.getitem.getattr', {'receiver': defs.ThisRef, 'property': defs.Variable}),
		('self.a.b', 'file_input.getattr', {'receiver': defs.Relay, 'property': defs.Variable}),
		('self.a().b', 'file_input.getattr', {'receiver': defs.FuncCall, 'property': defs.Variable}),
		('"".a', 'file_input.getattr', {'receiver': defs.String, 'property': defs.Variable}),
	])
	def test_relay(self, source: str, full_path: str, expected: dict[str, type[defs.Relay]]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Relay)
		self.assertEqual(type(node.receiver), expected['receiver'])
		self.assertEqual(type(node.prop), expected['property'])

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
		('class B(A): pass', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_var', defs.GeneralType),
		('class B(A[T]): pass', 'file_input.class_def.class_def_raw.typed_arguments.typed_argvalue.typed_getitem', defs.CustomType),
		('def func(a: int) -> None: pass', 'file_input.function_def.function_def_raw.parameters.paramvalue.typedparam.typed_var', defs.GeneralType),
		('def func(a: int) -> None: pass', 'file_input.function_def.function_def_raw.return_type.typed_none', defs.NullType),
	])
	def test_type(self, source: str, full_path: str, expected: type[defs.Type]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.Type)
		self.assertEqual(type(node), expected)

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.typed_getitem', {
			'value_type': 'int',
		}),
	])
	def test_list_type(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.ListType)
		self.assertEqual(node.value_type.tokens, expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.typed_getitem', {
			'key_type': 'Hoge.Values',
			'value_type': 'int',
		}),
	])
	def test_dict_type(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.DictType)
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
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.getitem', {
			'symbol': 'arr',
			'key': '0',
		}),
	])
	def test_indexer(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Indexer)
		self.assertEqual(node.receiver.tokens, expected['symbol'])
		self.assertEqual(node.key.tokens, expected['key'])

	@data_provider([
		('file_input.funccall', {
			'calls': 'pragma',
			'arguments': [
				{'value': "'once'"},
			],
			'calculated': [
				'<Variable: file_input.funccall.var>',
				'<Proxy: file_input.funccall.arguments.argvalue.__empty__>',
				'<String: file_input.funccall.arguments.argvalue.string>',
				'<Argument: file_input.funccall.arguments.argvalue>',
			],
		}),
	])
	def test_func_call(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.FuncCall)
		self.assertEqual(node.calls.tokens, expected['calls'])
		self.assertEqual(len(node.arguments), len(expected['arguments']))
		for index, argument in enumerate(node.arguments):
			in_expected = expected['arguments'][index]
			self.assertEqual(argument.value.tokens, in_expected['value'])

		self.assertEqual([str(node) for node in node.calculated()], expected['calculated'])

	# Operator

	@data_provider([
		('-1', 'file_input.factor', {'type': defs.Factor, 'value': '-1'}),
		('+1', 'file_input.factor', {'type': defs.Factor, 'value': '+1'}),
		('~1', 'file_input.factor', {'type': defs.Factor, 'value': '~1'}),
	])
	def test_unary_operator(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path).as_a(defs.UnaryOperator)
		self.assertEqual(type(node), expected['type'])
		self.assertEqual(node.tokens, expected['value'])

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
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[2].anno_assign.list', {
			'values': [
				{'value': '0', 'value_type': defs.Integer},
				{'value': '1', 'value_type': defs.Integer},
				{'value': '2', 'value_type': defs.Integer},
			],
		}),
	])
	def test_list(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.List)
		self.assertEqual(len(node.values), len(expected['values']))
		for index, value in enumerate(node.values):
			in_expected = expected['values'][index]
			self.assertEqual(value.tokens, in_expected['value'])
			self.assertEqual(type(value), in_expected['value_type'])

	@data_provider([
		('file_input.class_def[4].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].anno_assign.dict', {
			'items': [
				{'key': 'Hoge.Values.A', 'value': '0', 'value_type': defs.Integer},
				{'key': 'Hoge.Values.B', 'value': '1', 'value_type': defs.Integer},
			],
		}),
	])
	def test_dict(self, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.shared_nodes.by(full_path).as_a(defs.Dict)
		self.assertEqual(len(node.items), len(expected['items']))
		for index, item in enumerate(node.items):
			in_expected = expected['items'][index]
			self.assertEqual(item.first.tokens, in_expected['key'])
			self.assertEqual(item.second.tokens, in_expected['value'])
			self.assertEqual(type(item.second), in_expected['value_type'])
