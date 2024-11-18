import os
from typing import Any, cast
from unittest import TestCase

import yaml

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.render import Renderer


class Fixture:
	def __init__(self) -> None:
		# 効率化のためexampleのマッピングデータを利用
		trans_mapping = self.__load_trans_mapping(os.path.join(tranp_dir(), 'example/data/i18n.yml'))
		def translator(key: str) -> str:
			return trans_mapping.get(key, key)

		self.renderer = Renderer([os.path.join(tranp_dir(), 'data/cpp/template')], translator)

	def __load_trans_mapping(self, filepath: str) -> dict[str, str]:
		with open(filepath) as f:
			return cast(dict[str, str], yaml.safe_load(f))


class TestRenderer(TestCase):
	__fixture = Fixture()

	def assertRender(self, template: str, indent: int, vars: dict[str, Any], expected: str) -> None:
		"""Note: 文字列の比較は通例と逆配置にした方が見やすいため逆で利用"""
		actual = self.__fixture.renderer.render(template, indent=indent, vars=vars)
		self.assertEqual(expected, actual)

	@data_provider([
		(1, {'receiver': 'hoge', 'value': '1234'}, '\thoge = 1234;'),
		(2, {'receiver': 'hoge', 'value': '1234'}, '\t\thoge = 1234;'),
	])
	def test_render_indent(self, indent: int, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('assign/move_assign', indent, vars, expected)

	@data_provider([
		({'symbol': 'B', 'actual_type': 'A'}, 'using B = A;'),
	])
	def test_render_alt_class(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('alt_class', 0, vars, expected)

	@data_provider([
		({'label': '', 'value': 1}, '1'),
		({'label': 'a', 'value': 1}, '1'),
	])
	def test_render_argument(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('argument', 0, vars, expected)

	@data_provider([
		('move_assign', {'receiver': 'hoge', 'value': '1234'}, 'hoge = 1234;'),
		('move_assign', {'receiver': 'hoge'}, 'hoge;'),
		('anno_assign', {'receiver': 'hoge', 'value': '1234', 'var_type': 'int'}, 'int hoge = 1234;'),
		('anno_assign', {'receiver': 'hoge', 'var_type': 'int'}, 'int hoge;'),
		('aug_assign', {'receiver': 'hoge', 'value': '1234', 'operator': '+='}, 'hoge += 1234;'),
	])
	def test_render_assign(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'assign/{template}', 0, vars, expected)

	@data_provider([
		({'value_type': 'float', 'size': '10', 'default': '{100.0}', 'default_is_list': True}, 'std::vector<float>(10, 100.0)'),
		({'value_type': 'float', 'size': '10', 'default': 'std::vector<float>()', 'default_is_list': False}, 'std::vector<float>(10)'),
	])
	def test_render_binary_operator_fill_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator/fill_list', 0, vars, expected)

	@data_provider([
		({'left': 'key', 'operator': 'in', 'right': 'items', 'right_is_dict': True}, 'items.contains(key)'),
		({'left': 'key', 'operator': 'not.in', 'right': 'items', 'right_is_dict': True}, '(!items.contains(key))'),
		({'left': 'value', 'operator': 'in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) != values.end())'),
		({'left': 'value', 'operator': 'not.in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) == values.end())'),
	])
	def test_render_binary_operator_in(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator/in', 0, vars, expected)

	@data_provider([
		({'left': 'a', 'operator': 'is', 'right': 'b', 'left_var_type': 'int'}, 'a == b'),
		({'left': 'a', 'operator': 'is.not', 'right': 'b', 'left_var_type': 'int'}, 'a != b'),
		({'left': 'a', 'operator': 'and', 'right': 'b', 'left_var_type': 'int'}, 'a && b'),
		({'left': 'a', 'operator': 'or', 'right': 'b', 'left_var_type': 'int'}, 'a || b'),
		({'left': 'a', 'operator': '+', 'right': 'b', 'left_var_type': 'int'}, 'a + b'),
		({'left': 'a', 'operator': '-', 'right': 'b', 'left_var_type': 'int'}, 'a - b'),
		({'left': 'a', 'operator': '*', 'right': 'b', 'left_var_type': 'int'}, 'a * b'),
		({'left': 'a', 'operator': '/', 'right': 'b', 'left_var_type': 'int'}, 'a / b'),
		({'left': 'a', 'operator': '%', 'right': 'b', 'left_var_type': 'int'}, 'a % b'),
		({'left': 'a', 'operator': '%', 'right': 'b', 'left_var_type': 'float'}, 'fmod(a, b)'),
		({'left': 'a', 'operator': '%', 'right': 'b', 'left_var_type': 'double'}, 'fmod(a, b)'),
	])
	def test_render_binary_operator(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator/default', 0, vars, expected)

	@data_provider([
		({'statements': [ 'int x = 0;', 'int y = 0;', 'int z = 0;', ]}, 'int x = 0;\nint y = 0;\nint z = 0;'),
	])
	def test_render_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('block', 0, vars, expected)

	@data_provider([
		('default', {'type_name': 'Callable', 'parameters': ['int', 'float'], 'return_type': 'bool'}, 'std::function<bool(int, float)>'),
		('pluck_method', {'type_name': 'Callable', 'parameters': ['T', 'TArgs...'], 'return_type': 'void'}, 'typename PluckMethod<T, void, TArgs...>::method'),
	])
	def test_render_callable_type(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'callable_type/{template}', 0, vars, expected)

	@data_provider([
		({'var_type': 'Exception', 'symbol': 'e', 'statements': ['pass;']}, '} catch (Exception e) {\n\tpass;'),
	])
	def test_render_catch(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('catch', 0, vars, expected)

	@data_provider([
		({'accessor': 'public', 'decl_class_var': 'float a', 'decorators': []}, 'public: inline static float a'),
	])
	def test_render_class_decl_class_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/_decl_class_var', 0, vars, expected)

	@data_provider([
		({'accessor': 'public', 'var_type': 'float', 'symbol': 'a', 'decorators': []}, 'public: float a;'),
	])
	def test_render_class_decl_this_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/_decl_this_var', 0, vars, expected)

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
				'class Hoge : public Base, public Interface {',
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
				'class Hoge {',
				'	public: Hoge() {',
				'	}',
				'};',
			]),
		),
		(
			{
				'symbol': 'Struct',
				'decorators': [],
				'inherits': [],
				'vars': [],
				'comment': '',
				'statements': [],
				'is_struct': True,
			},
			'\n'.join([
				'/** Struct */',
				'struct Struct {',
				'};',
			]),
		),
	])
	def test_render_class(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/class', 0, vars, expected)

	@data_provider([
		(
			'list_comp',
			{
				'projection': 'value',
				'comp_for': 'auto& value : values',
				'condition': '',
				'projection_types': ['int'],
				'is_const': False,
				'is_addr_p': False,
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& value : values) {',
				'		__ret.push_back(value);',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
		(
			'list_comp',
			{
				'projection': 'value',
				'comp_for': 'auto& value : values',
				'condition': 'value == 1',
				'projection_types': ['int'],
				'is_const': False,
				'is_addr_p': False,
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& value : values) {',
				'		if (value == 1) {',
				'			__ret.push_back(value);',
				'		}',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
		(
			'dict_comp',
			{
				'projection_key': 'key',
				'projection_value': 'value',
				'comp_for': 'auto& [key, value] : items',
				'condition': '',
				'projection_types': ['int', 'float'],
				'is_const': False,
				'is_addr_p': False,
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
			'dict_comp',
			{
				'projection_key': 'key',
				'projection_value': 'value',
				'comp_for': 'auto& [key, value] : items',
				'condition': 'key == 1',
				'projection_types': ['int', 'float'],
				'is_const': False,
				'is_addr_p': False,
			},
			'\n'.join([
				'[&]() -> std::map<int, float> {',
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
	def test_render_comp(self, spec: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'comp/{spec}', 0, vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'is_const': False, 'is_addr_p': False}, 'auto& value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': True, 'is_addr_p': False}, 'const auto& value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': False, 'is_addr_p': True}, 'auto value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': True, 'is_addr_p': True}, 'const auto value : values'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': False, 'is_addr_p': False}, 'auto& [key, value] : items'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': True, 'is_addr_p': False}, 'const auto& [key, value] : items'),
	])
	def test_render_comp_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('comp/comp_for', 0, vars, expected)

	@data_provider([
		({'initializers': [], 'super_initializer': {}}, ''),
		({'initializers': [{'symbol': 'a', 'value': '1'}, {'symbol': 'b', 'value': '2'}], 'super_initializer': {}}, ' : a(1), b(2)'),
		({'initializers': [], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b)'),
		({'initializers': [{'symbol': 'a', 'value': '1'}], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b), a(1)'),
	])
	def test_render_constructor_initializer(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_initializer', 0, vars, expected)

	@data_provider([
		({'path': 'deco', 'arguments': ['a', 'b']}, 'deco(a, b)'),
	])
	def test_render_decorator(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('decorator', 0, vars, expected)

	@data_provider([
		({'targets': [{'receiver': 'l', 'key': '1', 'list_or_dict': 'list'}]}, 'l.erase(l.begin() + 1);'),
		({'targets': [{'receiver': 'd', 'key': '"a"', 'list_or_dict': 'dict'}]}, 'd.erase("a");'),
		({'targets': [{'receiver': 'l', 'key': '1', 'list_or_dict': 'list'}, {'receiver': 'd', 'key': '"a"', 'list_or_dict': 'dict'}]}, 'l.erase(l.begin() + 1);\nd.erase("a");'),
	])
	def test_render_delete(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'delete/default', 0, vars, expected)

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
					'note': '\n'.join([
						'note1',
						'note2',
					]),
					'examples': '\n'.join([
						'example1',
						'example2',
					]),
				},
			},
			'\n'.join([
				'/**',
				' * Description',
				' * @note',
				' * note1',
				' * note2',
				' * @example',
				' * example1',
				' * example2',
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
		({'statements': ['int x = 0;'], 'meta_header': '@tranp.meta: {"version":"1.0.0"}', 'module_path': 'path.to'}, '// @tranp.meta: {"version":"1.0.0"}\n#pragma once\nint x = 0;\n'),
	])
	def test_render_entrypoint(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('entrypoint', 0, vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Values',
				'decorators': ['deco(A, B)'],
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
		self.assertRender('class/enum', 0, vars, expected)

	@data_provider([
		({'symbols': ['key', 'value'], 'iterates': 'items', 'statements': []}, 'for (auto& [key, value] : items) {\n}'),
	])
	def test_render_for_dict(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/dict', 0, vars, expected)

	@data_provider([
		(
			{
				'symbols': ['index', 'value'],
				'iterates': 'items',
				'statements': [],
			},
			'\n'.join([
				'int index = 0;',
				'for (auto& value : items) {',
				'	index++;',
				'}',
			]),
		)
	])
	def test_render_for_enumerate(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/enumerate', 0, vars, expected)

	@data_provider([
		({'symbol': 'index', 'last_index': 'limit', 'statements': ['pass;']}, 'for (auto index = 0; index < limit; index++) {\n\tpass;\n}'),
	])
	def test_render_for_range(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/range', 0, vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': False}, 'for (auto& value : values) {\n\tpass;\n}'),
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': True}, 'for (const auto& value : values) {\n\tpass;\n}'),
	])
	def test_render_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/default', 0, vars, expected)

	@data_provider([
		({'arguments': ['"<string>"']}, '#include <string>'),
		({'arguments': ['"' '"path/to/module.h"' '"']}, '#include "path/to/module.h"'),
	])
	def test_render_func_call_c_include(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_include', 0, vars, expected)

	@data_provider([
		({'arguments': ['"MACRO()"']}, 'MACRO()'),
	])
	def test_render_func_call_c_macro(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_macro', 0, vars, expected)

	@data_provider([
		({'arguments': ['"once"']}, '#pragma once'),
	])
	def test_render_func_call_c_pragma(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_pragma', 0, vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['1.0f'], 'is_statement': True}, 'static_cast<int>(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_bin_to_bin', 0, vars, expected)

	@data_provider([
		({'arguments': ['1.0f'], 'is_statement': True}, 'std::to_string(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_str(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_bin_to_str', 0, vars, expected)

	@data_provider([
		({'arguments': ['"A"'], 'is_statement': True}, "'A';"),
		({'arguments': ['string[0]'], 'is_statement': True}, "string[0];"),
	])
	def test_render_func_call_cast_char(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_char', 0, vars, expected)

	@data_provider([
		({'arguments': ['iterates'], 'is_statement': True}, 'iterates;'),
	])
	def test_render_func_call_cast_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_list', 0, vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['"1"'], 'is_statement': True}, 'atoi("1");'),
		({'var_type': 'float', 'arguments': ['"1.0"'], 'is_statement': True}, 'atof("1.0");'),
	])
	def test_render_func_call_cast_str_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_str_to_bin', 0, vars, expected)

	@data_provider([
		({'var_type': 'std::string', 'arguments': ['"1"'], 'is_statement': True}, 'std::string("1");'),
	])
	def test_render_func_call_cast_str_to_str(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_str_to_str', 0, vars, expected)

	@data_provider([
		({'arguments': ['A(0)'], 'is_statement': True}, 'new A(0);'),
	])
	def test_render_func_call_cvar_new_p(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_p', 0, vars, expected)

	@data_provider([
		({'var_type': 'std::vector<A>', 'initializer': '{0}, {1}', 'is_statement': True}, 'std::shared_ptr<std::vector<A>>(new std::vector<A>({0}, {1}));'),
	])
	def test_render_func_call_cvar_new_sp_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_sp_list', 0, vars, expected)

	@data_provider([
		({'var_type': 'A', 'initializer': '0', 'is_statement': True}, 'std::make_shared<A>(0);'),
	])
	def test_render_func_call_cvar_new_sp(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_sp', 0, vars, expected)

	@data_provider([
		({'var_type': 'int', 'is_statement': True}, 'std::shared_ptr<int>();'),
	])
	def test_render_func_call_cvar_sp_empty(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_sp_empty', 0, vars, expected)

	@data_provider([
		({'cvar_type': 'CP', 'arguments': ['n'], 'is_statement': True}, '(&(n));'),
		({'cvar_type': 'CPConst', 'arguments': ['n'], 'is_statement': True}, '(&(n));'),
		({'cvar_type': 'CP', 'arguments': ['this'], 'is_statement': True}, 'this;'),
		({'cvar_type': 'CPConst', 'arguments': ['this'], 'is_statement': True}, 'this;'),
		({'cvar_type': 'CP', 'arguments': ['this->n'], 'is_statement': True}, '(&(this->n));'),
		({'cvar_type': 'CPConst', 'arguments': ['this->n'], 'is_statement': True}, '(&(this->n));'),
		({'cvar_type': 'CSP', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CSPConst', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CRef', 'arguments': ['n'], 'is_statement': True}, 'n;'),
		({'cvar_type': 'CRefConst', 'arguments': ['n'], 'is_statement': True}, 'n;'),
	])
	def test_render_func_call_cvar_to(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_to', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
				'operator': '.',
				'is_statement': True,
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& [__key, _] : items) {',
				'		__ret.push_back(__key);',
				'	}',
				'	return __ret;',
				'}();',
			]),
		),
	])
	def test_render_func_call_dict_keys(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/dict_keys', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
				'operator': '.',
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
		self.assertRender('func_call/dict_pop', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'items',
				'operator': '.',
				'is_statement': True,
			},
			'\n'.join([
				'[&]() -> std::vector<int> {',
				'	std::vector<int> __ret;',
				'	for (auto& [_, __value] : items) {',
				'		__ret.push_back(__value);',
				'	}',
				'	return __ret;',
				'}();',
			]),
		),
	])
	def test_render_func_call_dict_values(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/dict_values', 0, vars, expected)

	@data_provider([
		({'calls': 'static_cast', 'arguments': ['Class*', 'p'], 'is_statement': True}, 'static_cast<Class*>(p);'),
	])
	def test_render_func_call_generic_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/generic_call', 0, vars, expected)

	@data_provider([
		({'arguments': ['values'], 'is_statement': True}, 'values.size();'),
	])
	def test_render_func_call_len(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/len', 0, vars, expected)

	@data_provider([
		({'receiver': 'values', 'operator': '.', 'arguments': ['1', 'value']}, 'values.insert(values.begin() + 1, value)'),
	])
	def test_render_func_call_list_insert(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/list_insert', 0, vars, expected)

	@data_provider([
		({'receiver': 'values', 'operator': '.', 'arguments': ['values2']}, 'values.insert(values.end(), values2)'),
	])
	def test_render_func_call_list_extend(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/list_extend', 0, vars, expected)

	@data_provider([
		(
			{
				'var_type': 'int',
				'receiver': 'values',
				'operator': '.',
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
				'operator': '.',
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
		self.assertRender('func_call/list_pop', 0, vars, expected)

	@data_provider([
		({'arguments': ['"%d, %f"', '1', '1.0f'], 'is_statement': True}, 'printf("%d, %f", 1, 1.0f);'),
	])
	def test_render_func_call_print(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/print', 0, vars, expected)

	@data_provider([
		({'calls': 'A.func', 'arguments': ['1 + 2', 'A.value']}, 'A.func(1 + 2, A.value)'),
	])
	def test_render_func_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/default', 0, vars, expected)

	@data_provider([
		({'statements': ['pass;']}, '{\n\tpass;\n}'),
	])
	def test_render_function_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_block', 0, vars, expected)

	@data_provider([
		({'parameter': 'int n', 'decorators': []}, 'int n'),
		({'parameter': 'int n', 'decorators': ['Embed.param("n", mutable=false)']}, 'const int& n'),
		({'parameter': 'int n = 1', 'decorators': []}, 'int n = 1'),
		({'parameter': 'int n = 1', 'decorators': ['Embed.param("n", mutable=false)']}, 'const int& n = 1'),
		({'parameter': 'const int& n', 'decorators': []}, 'const int& n'),
		({'parameter': 'const int& n', 'decorators': ['Embed.param("n", mutable=false)']}, 'const int& n'),
	])
	def test_render_function_definition_param(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_definition_param', 0, vars, expected)

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
			},
			'\n'.join([
				'auto closure = [&](std::string text, int value = 1) -> int {',
				'	return value + 1;',
				'};',
			]),
		),
		(
			'closure',
			{
				'symbol': 'closure_bind',
				'decorators': ['Embed.closure_bind(this, a, b)'],
				'parameters': ['std::string text', 'int value = 1'],
				'return_type': 'int',
				# 'comment': '',
				'statements': ['return value + 1;'],
				# 'template_types': [],
				# closure only
			},
			'\n'.join([
				'auto closure_bind = [this, a, b](std::string text, int value = 1) mutable -> int {',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
				# constructor only
				'initializers': [{'symbol': 'a', 'value': '1'}, {'symbol': 'b', 'value': ''}],
				'super_initializer': {'parent': 'Base', 'arguments': 'base_n'},
			},
			'\n'.join([
				'public:',
				'/** __init__ */',
				'Hoge(int base_n = 1, int value = 2) : Base(base_n), a(1), b({}) {',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': True,
				'is_override': False,
				'allow_override': False,
				# constructor only
				'initializers': [],
				'super_initializer': {},
			},
			'\n'.join([
				'public:',
				'/** __init__ */',
				'template<typename T>',
				'virtual Hoge() = 0;',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** static_method */',
				'static int static_method() {',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** static_method */',
				'template<typename T>',
				'static void static_method() {}',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** method */',
				'void method(int value = 1) {',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': True,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** pure_virtual_method */',
				'virtual void pure_virtual_method(int value = 1) = 0;',
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
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': True,
			},
			'\n'.join([
				'public:',
				'/** allow_override_method */',
				'virtual void allow_override_method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'overrided_method',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': [],
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': True,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** overrided_method */',
				'void overrided_method(int value = 1) override {',
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
				'template_types': ['T', 'T2', 'TArgs...'],
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'public:',
				'/** template_method */',
				'template<typename T, typename T2, typename ...TArgs>',
				'void template_method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'decorated_method',
				'decorators': ['deco(A, B)', 'Embed.private()', 'Embed.pure()'],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'comment': '',
				'statements': ['this->x = value;'],
				'template_types': [],
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
			},
			'\n'.join([
				'private:',
				'/** decorated_method */',
				'void decorated_method(int value = 1) const {',
				'	this->x = value;',
				'}',
			]),
		),
	])
	def test_render_function(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'function/{template}', 0, vars, expected)

	@data_provider([
		({'module_path': 'module.path.to', 'import_dir': '', 'replace_dir': ''}, '// #include "module/path/to.h"'),
		({'module_path': 'module.path.to', 'import_dir': 'module/path/', 'replace_dir': 'path/'}, '#include "path/to.h"'),
	])
	def test_render_import(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('import', 0, vars, expected)

	@data_provider([
		('cvar', {'var_type': 'int*'}, 'int*'),
		('class', {'var_type': 'int'}, 'int'),
		('default', {'receiver': 'n', 'key': '0'}, 'n[0]'),
		('default', {'receiver': 'n', 'key': '0', 'is_statement': True}, 'n[0];'),
		('slice_string', {'receiver': 's', 'keys': ['0', '1']}, 's.substr(0, 1)'),
		('slice_string', {'receiver': 's', 'keys': ['1', '2']}, 's.substr(1, 2 - (1))'),
		('slice_string', {'receiver': 's', 'keys': ['1']}, 's.substr(1, s.size() - (1))'),
		('tuple', {'receiver': 't', 'key': '0'}, 'std::get<0>(t)'),
	])
	def test_render_indexer(self, spec: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'indexer/{spec}', 0, vars, expected)

	@data_provider([
		({'values': ['1234', '2345']}, '{\n\t{1234},\n\t{2345},\n}'),
		({'values': []}, '{}'),
	])
	def test_render_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('list', 0, vars, expected)

	@data_provider([
		({'receiver': 'raw', 'move': 'ToAddress'}, '(&(raw))'),
		({'receiver': 'addr', 'move': 'ToActual'}, '(*(addr))'),
		({'receiver': 'sp', 'move': 'UnpackSp'}, '(sp).get()'),
		({'receiver': 'raw', 'move': 'Copy'}, 'raw'),
	])
	def test_render_relay_cvar_to(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/cvar_to', 0, vars, expected)

	@data_provider([
		({'receiver': 'a', 'operator': 'Raw', 'prop': 'b', 'is_property': False}, 'a.b'),
		({'receiver': 'a', 'operator': 'Raw', 'prop': 'b', 'is_property': True}, 'a.b()'),
		({'receiver': 'a', 'operator': 'Address', 'prop': 'b', 'is_property': False}, 'a->b'),
		({'receiver': 'a', 'operator': 'Address', 'prop': 'b', 'is_property': True}, 'a->b()'),
		({'receiver': 'A', 'operator': 'Static', 'prop': 'B', 'is_property': False}, 'A::B'),
	])
	def test_render_relay_default(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/default', 0, vars, expected)

	@data_provider([
		({'prop': '__name__', 'literal': 'A'}, '"A"'),
		({'prop': '__module_path__', 'literal': 'module.path.to.A'}, '"module.path.to.A"'),
		({'prop': '__qualname__', 'literal': 'A.func'}, '"A.func"'),
	])
	def test_render_relay_literalize(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/literalize', 0, vars, expected)

	@data_provider([
		({'return_value': '(1 + 2)'}, 'return (1 + 2);'),
		({'return_value': ''}, 'return;'),
	])
	def test_render_return(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('return', 0, vars, expected)

	@data_provider([
		({'throws': 'e', 'via': '', 'is_new': False}, 'throw e;'),
		({'throws': 'std::exception()', 'via': 'e', 'is_new': True}, 'throw new std::exception();'),
	])
	def test_render_throw(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('throw', 0, vars, expected)

	@data_provider([
		({'statements': ['pass;'], 'catches': []}, 'try {\n\tpass;\n}'),
		({'statements': ['pass;'], 'catches': ['} catch (std::exception e) {\n\tthrow e;']}, 'try {\n\tpass;\n} catch (std::exception e) {\n\tthrow e;\n}'),
	])
	def test_render_try(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('try', 0, vars, expected)

	@data_provider([
		('default', {'type_name': 'int'}, 'int'),
		('default', {'type_name': 'str'}, 'std::string'),
		('template', {'type_name': 'T', 'definition_type': 'TypeVar'}, 'T'),
		('template', {'type_name': 'TArgs', 'definition_type': 'TypeVarTuple'}, 'TArgs...'),
		('template', {'type_name': 'P', 'definition_type': 'ParamSpec'}, 'P'),
	])
	def test_render_var_of_type(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'var_of_type/{template}', 0, vars, expected)
