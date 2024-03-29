import os
from typing import Any
from unittest import TestCase

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.translation import to_classes_alias, to_cpp_alias
from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.render import Renderer


class Fixture:
	@classmethod
	def renderer(cls) -> Renderer:
		trans_mapping = {
			to_classes_alias('dict.in'): 'contains',
			to_classes_alias('dict'): 'std::map',
			to_classes_alias('list'): 'std::vector',
			to_classes_alias('list.append'): 'push_back',
			to_classes_alias('list.remove'): 'erase',
			to_classes_alias('print'): 'printf',
			to_classes_alias('str'): 'std::string',
			to_cpp_alias('container.size'): 'size',
			to_cpp_alias('make_shared'): 'std::make_shared',
			to_cpp_alias('map.erase'): 'erase',
			to_cpp_alias('shared_ptr'): 'std::shared_ptr',
			to_cpp_alias('to_string'): 'std::to_string',
			to_cpp_alias('vector.begin'): 'begin',
			to_cpp_alias('vector.end'): 'end',
		}
		def translator(key: str) -> str:
			return trans_mapping.get(key, key)

		return Renderer([os.path.join(tranp_dir(), 'data/cpp/template')], translator)


class TestRenderer(TestCase):
	def assertRender(self, template: str, indent: int, vars: dict[str, Any], expected: str) -> None:
		renderer = Fixture.renderer()
		actual = renderer.render(template, indent=indent, vars=vars)
		self.assertEqual(actual, expected)

	@data_provider([
		(1, {'receiver': 'hoge', 'value': '1234'}, '\thoge = 1234;'),
		(2, {'receiver': 'hoge', 'value': '1234'}, '\t\thoge = 1234;'),
	])
	def test_render_indent(self, indent: int, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('move_assign', indent, vars, expected)

	@data_provider([
		({'symbol': 'B', 'actual_type': 'A'}, 'using B = A;'),
	])
	def test_render_alt_class(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('alt_class', 0, vars, expected)

	@data_provider([
		('move_assign', {'receiver': 'hoge', 'value': '1234'}, 'hoge = 1234;'),
		('move_assign', {'receiver': 'hoge'}, 'hoge;'),
		('anno_assign', {'receiver': 'hoge', 'value': '1234', 'var_type': 'int'}, 'int hoge = 1234;'),
		('anno_assign', {'receiver': 'hoge', 'var_type': 'int'}, 'int hoge;'),
		('aug_assign', {'receiver': 'hoge', 'value': '1234', 'operator': '+='}, 'hoge += 1234;'),
	])
	def test_render_assign(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(template, 0, vars, expected)

	@data_provider([
		({'value_type': 'float', 'size': '10', 'default': '100.0'}, 'std::vector<float>(10, 100.0)'),
	])
	def test_render_binary_operator_fill_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator_fill_list', 0, vars, expected)

	@data_provider([
		({'left': 'key', 'operator': 'in', 'right': 'items', 'right_is_dict': True}, 'items.contains(key)'),
		({'left': 'key', 'operator': 'not.in', 'right': 'items', 'right_is_dict': True}, '(!items.contains(key))'),
		({'left': 'value', 'operator': 'in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) != values.end())'),
		({'left': 'value', 'operator': 'not.in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) == values.end())'),
		({'left': 'a', 'operator': 'is', 'right': 'b', 'right_is_dict': False}, 'a == b'),
		({'left': 'a', 'operator': 'is.not', 'right': 'b', 'right_is_dict': False}, 'a != b'),
		({'left': 'a', 'operator': 'and', 'right': 'b', 'right_is_dict': False}, 'a && b'),
		({'left': 'a', 'operator': 'or', 'right': 'b', 'right_is_dict': False}, 'a || b'),
		({'left': 'a', 'operator': '+', 'right': 'b', 'right_is_dict': False}, 'a + b'),
		({'left': 'a', 'operator': '-', 'right': 'b', 'right_is_dict': False}, 'a - b'),
		({'left': 'a', 'operator': '*', 'right': 'b', 'right_is_dict': False}, 'a * b'),
		({'left': 'a', 'operator': '/', 'right': 'b', 'right_is_dict': False}, 'a / b'),
	])
	def test_render_binary_operator(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator', 0, vars, expected)

	@data_provider([
		({'statements': [ 'int x = 0;', 'int y = 0;', 'int z = 0;', ]}, 'int x = 0;\nint y = 0;\nint z = 0;'),
	])
	def test_render_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('block', 0, vars, expected)

	@data_provider([
		({'var_type': 'Exception', 'symbol': 'e', 'block': 'pass;'}, 'catch (Exception e) {\n\tpass;\n}'),
	])
	def test_render_catch(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('catch', 0, vars, expected)

	@data_provider([
		({'access': 'public', 'decl_class_var': 'float a'}, 'public: static float a'),
	])
	def test_render_class_decl_class_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class_decl_class_var', 0, vars, expected)

	@data_provider([
		({'access': 'public', 'var_type': 'float', 'symbol': 'a'}, 'public: float a;'),
	])
	def test_render_class_decl_this_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class_decl_this_var', 0, vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Hoge',
				'decorators': ['deco(A, A.B)'],
				'inherits': ['Base', 'Interface'],
				'vars': [
					'private: int __value;',
					'private: std::string __text;',
				],
				'comment': '',
				'statements': [
					'\n'.join([
						'public: Hoge() {',
						'	int hoge = 1234;',
						'	int fuga = 2345;',
						'}',
					]),
				],
			},
			'\n'.join([
				'/** Hoge */',
				'deco(A, A.B)',
				'class Hoge : public Base, Interface {',
				'	private: int __value;',
				'	private: std::string __text;',
				'	public: Hoge() {',
				'		int hoge = 1234;',
				'		int fuga = 2345;',
				'	}',
				'};',
			]),
		),
		(
			{
				'symbol': 'Hoge',
				'decorators': [],
				'inherits': [],
				'vars': [],
				'comment': '',
				'statements': [
					'\n'.join([
						'public: Hoge() {',
						'}',
					]),
				],
			},
			'\n'.join([
				'/** Hoge */',
				'class Hoge {',
				'	public: Hoge() {',
				'	}',
				'};',
			]),
		),
		(
			{
				'symbol': 'Hoge',
				'decorators': [],
				'inherits': [],
				'vars': [],
				'comment': '\n'.join([
					'/**',
					' * Description',
					' */',
				]),
				'statements': [
					'\n'.join([
						'public: Hoge() {',
						'}',
					]),
				],
			},
			'\n'.join([
				'/**',
				' * Description',
				' */',
				'class Hoge {',
				'	public: Hoge() {',
				'	}',
				'};',
			]),
		),
		(
			{
				'symbol': 'Hoge',
				'decorators': ['deco(A, A.B)'],
				'inherits': [],
				'vars': [],
				'comment': '\n'.join([
					'/**',
					' * Description',
					' */',
				]),
				'statements': [
					'\n'.join([
						'public: Hoge() {',
						'}',
					]),
				],
			},
			'\n'.join([
				'/**',
				' * Description',
				' */',
				'deco(A, A.B)',
				'class Hoge {',
				'	public: Hoge() {',
				'	}',
				'};',
			]),
		),
	])
	def test_render_class(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class', 0, vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'is_const': False}, 'auto& value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': True}, 'const auto& value : values'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': False}, 'auto& [key, value] : items'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': True}, 'const auto& [key, value] : items'),
	])
	def test_render_comp_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('comp_for', 0, vars, expected)

	@data_provider([
		({'initializers': [], 'super_initializer': {}}, ''),
		({'initializers': [{'symbol': 'a', 'value': '1'}, {'symbol': 'b', 'value': '2'}], 'super_initializer': {}}, ' : a(1), b(2)'),
		({'initializers': [], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b)'),
		({'initializers': [{'symbol': 'a', 'value': '1'}], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b), a(1)'),
	])
	def test_render_constructor_initializer(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('constructor_initializer', 0, vars, expected)

	@data_provider([
		({'path': 'classmethod', 'arguments': []}, ''),
		({'path': 'abstractmethod', 'arguments': []}, ''),
		({'path': '__alias__', 'arguments': []}, ''),
		({'path': '__allow_override__', 'arguments': []}, ''),
		({'path': 'deco', 'arguments': ['a', 'b']}, 'deco(a, b)'),
	])
	def test_render_decorator(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('decorator', 0, vars, expected)

	@data_provider([
		(
			{
				'projection': '{key, value}',
				'comp_for': 'auto& [key, value] : items',
				'condition': '',
				'projection_types': ['int', 'float'],
				'binded_this': False,
			},
			'\n'.join([
				'[&]() -> std::map<int, float> {',
				'	std::map<int, float> __ret;',
				'	for (auto& [key, value] : items) {',
				'		__ret[key] = value;',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
		(
			{
				'projection': '{key, value}',
				'comp_for': 'auto& [key, value] : items',
				'condition': 'key == 1',
				'projection_types': ['int', 'float'],
				'binded_this': True,
			},
			'\n'.join([
				'[this, &]() -> std::map<int, float> {',
				'	std::map<int, float> __ret;',
				'	for (auto& [key, value] : items) {',
				'		if (key == 1) {',
				'			__ret[key] = value;',
				'		}',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
	])
	def test_render_dict_comp(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('dict_comp', 0, vars, expected)

	@data_provider([
		({'key_type': 'int', 'value_type': 'float'}, 'std::map<int, float>'),
	])
	def test_render_dict_type(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('dict_type', 0, vars, expected)

	@data_provider([
		({'items': ['{hoge, 1}','{fuga, 2}']}, '{\n\t{hoge, 1},\n\t{fuga, 2},\n}'),
		({'items': []}, '{}'),
	])
	def test_render_dict(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('dict', 0, vars, expected)

	@data_provider([
		(
			{
				'data': {
					'description': 'Description',
					'attributes': [],
					'args': [
						{'name': 'a', 'type': 'A', 'description': 'A desc'},
						{'name': 'b', 'type': 'B', 'description': 'B desc'},
					],
					'returns': {'type': 'R', 'description': 'R desc'},
					'raises': [
						{'type': 'E1', 'description': 'E1 desc'},
						{'type': 'E2', 'description': 'E2 desc'},
					],
					'note': 'Some note',
					'examples': 'Some example',
				},
			},
			'\n'.join([
				'/**',
				' * Description',
				' * @param a A desc',
				' * @param b B desc',
				' * @return R desc',
				' * @throw E1 E1 desc',
				' * @throw E2 E2 desc',
				' * @note Some note',
				' * @example Some example',
				' */',
			]),
		),
		(
			{
				'data': {
					'description': 'Description',
					'attributes': [
						{'name': 'a', 'type': 'A', 'description': 'A desc'},
						{'name': 'b', 'type': 'B', 'description': 'B desc'},
					],
					'args': [],
					'returns': {'type': '', 'description': ''},
					'raises': [],
					'note': '',
					'examples': '',
				},
			},
			'\n'.join([
				'/**',
				' * Description',
				' */',
			]),
		),
	])
	def test_render_doc_string(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('doc_string', 0, vars, expected)

	@data_provider([
		({'condition': 'value == 1', 'statements': ['pass;']}, '} else if (value == 1) {\n\tpass;'),
	])
	def test_render_else_if(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('else_if', 0, vars, expected)

	@data_provider([
		({'statements': ['pass;']}, '} else {\n\tpass;'),
	])
	def test_render_else(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('else', 0, vars, expected)

	@data_provider([
		({'meta_header': '@tranp.meta: {"version":"1.0.0"}', 'statements': [ 'int x = 0;', ]}, '// @tranp.meta: {"version":"1.0.0"}\nint x = 0;\n'),
	])
	def test_render_entrypoint(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('entrypoint', 0, vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Values',
				'comment': '',
				'statements': [
					'int A = 0;',
					'int B = 1;',
				],
			},
			'\n'.join([
				'/** Values */',
				'enum class Values {',
				'	A = 0,',
				'	B = 1,',
				'};',
			]),
		),
	])
	def test_render_enum(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('enum', 0, vars, expected)

	@data_provider([
		({'symbols': ['key', 'value'], 'iterates': 'items', 'statements': ['pass;']}, 'for (auto& [key, value] : items) {\n\tpass;\n}'),
	])
	def test_render_for_dict_items(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for_dict_items', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'float',
				'iterates': 'items',
			},
			'\n'.join([
				'[&]() -> std::map<int, float> {',
				'	std::map<int, float> __ret;',
				'	int __index = 0;',
				'	for (auto& __entry : items) {',
				'		__ret[__index++] = __entry;',
				'	}',
				'	return __ret;',
				'}()',
			]),
		)
	])
	def test_render_for_enumerate_iterates(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for_enumerate_iterates', 0, vars, expected)

	@data_provider([
		(
			{
				'symbols': ['key', 'value'],
				'var_type': 'float',
				'iterates': 'items',
				'statements': ['pass;'],
			},
			'\n'.join([
				'for (auto& [key, value] : [&]() -> std::map<int, float> {',
				'	std::map<int, float> __ret;',
				'	int __index = 0;',
				'	for (auto& __entry : items) {',
				'		__ret[__index++] = __entry;',
				'	}',
				'	return __ret;',
				'}()) {',
				'	pass;',
				'}',
			]),
		)
	])
	def test_render_for_enumerate(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for_enumerate', 0, vars, expected)

	@data_provider([
		({'symbol': 'index', 'last_index': 'limit', 'statements': ['pass;']}, 'for (auto index = 0; i < limit; index++) {\n\tpass;\n}'),
	])
	def test_render_for_range(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for_range', 0, vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': False}, 'for (auto& value : values) {\n\tpass;\n}'),
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': True}, 'for (const auto& value : values) {\n\tpass;\n}'),
	])
	def test_render_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for', 0, vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['1.0f'], 'is_statement': True}, '(int)(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_cast_bin_to_bin', 0, vars, expected)

	@data_provider([
		({'arguments': ['1.0f'], 'is_statement': True}, 'std::to_string(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_str(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_cast_bin_to_str', 0, vars, expected)

	@data_provider([
		({'arguments': ['iterates'], 'is_statement': True}, 'iterates;'),
	])
	def test_render_func_call_cast_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_cast_list', 0, vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['"1"'], 'is_statement': True}, 'atoi("1");'),
		({'var_type': 'float', 'arguments': ['"1.0"'], 'is_statement': True}, 'atof("1.0");'),
	])
	def test_render_func_call_cast_str_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_cast_str_to_bin', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& [__key, _] : items) {',
				'		__ret.push_back(__key);',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
	])
	def test_render_func_call_dict_keys(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_dict_keys', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
				'arguments': ['key'],
				'is_statement': True,
			},
			'\n'.join([
				'[&]() -> int {',
				'	auto __copy = items[key];',
				'	items.erase(key);',
				'	return __copy;',
				'}();',
			]),
		),
	])
	def test_render_func_call_dict_pop(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_dict_pop', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& [_, __value] : items) {',
				'		__ret.push_back(__value);',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
	])
	def test_render_func_call_dict_values(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_dict_values', 0, vars, expected)

	@data_provider([
		({'arguments': ["'" '#include "path/to/module.h"' "'"]}, '#include "path/to/module.h"'),
		({'arguments': ['"#pragma once"']}, '#pragma once'),
		({'arguments': ['"#ifdef A"']}, '#ifdef A'),
		({'arguments': ['"#endif"']}, '#endif'),
	])
	def test_render_func_call_directive(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_directive', 0, vars, expected)

	@data_provider([
		({'arguments': ['values'], 'is_statement': True}, 'values.size();'),
	])
	def test_render_func_call_len(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_len', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'values',
				'arguments': ['0'],
				'is_statement': True,
			},
			'\n'.join([
				'[&]() -> int {',
				'	auto __iter = values.begin() + 0;',
				'	auto __copy = *__iter;',
				'	values.erase(__iter);',
				'	return __copy;',
				'}();',
			]),
		),
		(
			{
				'var_type': 'int',
				'receiver': 'values',
				'arguments': [],
				'is_statement': True,
			},
			'\n'.join([
				'[&]() -> int {',
				'	auto __iter = values.end() - 1;',
				'	auto __copy = *__iter;',
				'	values.erase(__iter);',
				'	return __copy;',
				'}();',
			]),
		),
	])
	def test_render_func_call_list_pop(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_list_pop', 0, vars, expected)

	@data_provider([
		({'arguments': ['A(0)'], 'is_statement': True}, 'new A(0);'),
	])
	def test_render_func_call_new_cvar_p(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_new_cvar_p', 0, vars, expected)

	@data_provider([
		({'var_type': 'std::vector<A>', 'initializer': '{0}, {1}', 'is_statement': True}, 'std::shared_ptr<std::vector<A>>(new std::vector<A>({0}, {1}));'),
	])
	def test_render_func_call_new_cvar_sp_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_new_cvar_sp_list', 0, vars, expected)

	@data_provider([
		({'var_type': 'A', 'initializer': '0', 'is_statement': True}, 'std::make_shared<A>(0);'),
	])
	def test_render_func_call_new_cvar_sp(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_new_cvar_sp', 0, vars, expected)

	@data_provider([
		({'arguments': ['"%d, %f"', '1', '1.0f'], 'is_statement': True}, 'printf("%d, %f", 1, 1.0f);'),
	])
	def test_render_func_call_print(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_print', 0, vars, expected)

	@data_provider([
		({'cvar_type': 'CP', 'arguments': ['n'], 'is_statement': True}, '&(n);'),
		({'cvar_type': 'CPConst', 'arguments': ['n'], 'is_statement': True}, '&(n);'),
		({'cvar_type': 'CSP', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CSPConst', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CRef', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CRefConst', 'arguments': ['n'], 'is_statement': True}, 'n;'),
	])
	def test_render_func_call_to_cvar(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call_to_cvar', 0, vars, expected)

	@data_provider([
		({'calls': 'A.func', 'arguments': ['1 + 2', 'A.value']}, 'A.func(1 + 2, A.value)'),
	])
	def test_render_func_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call', 0, vars, expected)

	@data_provider([
		({'statements': ['pass;']}, '{\n\tpass;\n}'),
	])
	def test_render_function_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function_block', 0, vars, expected)

	@data_provider([
		(
			'function',
			{
				'symbol': 'func',
				'decorators': ['deco(A, B)'],
				'parameters': ['std::string text', 'int value = 1'],
				'return_type': 'int',
				'comment': '',
				'statements': ['return value + 1;'],
				'template_types': ['T'],
			},
			'\n'.join([
				'/** func */',
				'template<typename T>',
				'deco(A, B)',
				'int func(std::string text, int value = 1) {',
				'	return value + 1;',
				'}',
			]),
		),
		(
			'closure',
			{
				'symbol': 'closure',
				# 'decorators': [],
				'parameters': ['std::string text', 'int value = 1'],
				'return_type': 'int',
				# 'comment': '',
				'statements': ['return value + 1;'],
				# 'template_types': [],
				# closure only
				'binded_this': True,
			},
			'\n'.join([
				'auto closure = [this, &](std::string text, int value = 1) -> int {',
				'	return value + 1;',
				'};',
			]),
		),
		(
			'constructor',
			{
				'symbol': '__init__',
				'decorators': [],
				'parameters': ['int base_n = 1', 'int value = 2'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': [],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': False,
				# constructor only
				'initializers': [{'symbol': 'a', 'value': '1'}],
				'super_initializer': {'parent': 'Base', 'arguments': 'base_n'},
			},
			'\n'.join([
				'/** Constructor */',
				'public: Hoge(int base_n = 1, int value = 2) : Base(base_n), a(1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'constructor',
			{
				'symbol': '__init__',
				'decorators': ['deco(A, B)'],
				'parameters': [],
				'return_type': 'void',
				'comment': '',
				'statements': [],
				'template_types': ['T'],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': True,
				'allow_override': False,
				# constructor only
				'initializers': [],
				'super_initializer': {},
			},
			'\n'.join([
				'/** Constructor */',
				'public:',
				'template<typename T>',
				'deco(A, B)',
				'virtual Hoge();',
			]),
		),
		(
			'class_method',
			{
				'symbol': 'static_method',
				'decorators': [],
				'parameters': [],
				'return_type': 'int',
				'comment': '',
				'statements': ['return 1;'],
				'template_types': [],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': False,
			},
			'\n'.join([
				'/** static_method */',
				'public: static int static_method() {',
				'	return 1;',
				'}',
			]),
		),
		(
			'class_method',
			{
				'symbol': 'static_method',
				'decorators': ['deco(A, B)'],
				'parameters': [],
				'return_type': 'void',
				'comment': '',
				'statements': [],
				'template_types': ['T'],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': False,
			},
			'\n'.join([
				'/** static_method */',
				'public:',
				'template<typename T>',
				'deco(A, B)',
				'static void static_method() {',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'method',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': [],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': False,
			},
			'\n'.join([
				'/** method */',
				'public: void method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'pure_virtual_method',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': [],
				'template_types': [],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': True,
				'allow_override': False,
			},
			'\n'.join([
				'/** pure_virtual_method */',
				'public: virtual void pure_virtual_method(int value = 1);',
			]),
		),
		(
			'method',
			{
				'symbol': 'allow_override_method',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': [],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': True,
			},
			'\n'.join([
				'/** allow_override_method */',
				'public: virtual void allow_override_method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'template_method',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': ['T', 'T2'],
				# belongs class only
				'access': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'allow_override': False,
			},
			'\n'.join([
				'/** template_method */',
				'public:',
				'template<typename T>',
				'template<typename T2>',
				'void template_method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
	])
	def test_render_function(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(template, 0, vars, expected)

	@data_provider([
		({'module_path': 'module.path.to'}, '// #include "module/path/to.h"'),
	])
	def test_render_import(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('import', 0, vars, expected)

	@data_provider([
		({'values': ['1234', '2345']}, '{\n\t{1234},\n\t{2345},\n}'),
		({'values': []}, '{}'),
	])
	def test_render_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('list', 0, vars, expected)

	@data_provider([
		({'return_value': '(1 + 2)'}, 'return (1 + 2);'),
	])
	def test_render_return(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('return', 0, vars, expected)
