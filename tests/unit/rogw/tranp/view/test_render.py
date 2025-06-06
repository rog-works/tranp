import os
from typing import Any, cast
from unittest import TestCase

import yaml

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.implements.cpp.providers.view import renderer_helper_provider_cpp
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.translator import Translator
from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.render import Renderer, RendererSetting


class Fixture:
	def __init__(self) -> None:
		# 効率化のためexampleのマッピングデータを利用
		trans_mapping = self.__load_trans_mapping(os.path.join(tranp_dir(), 'data/i18n.yml'))

		@duck_typed(Translator)
		def translator(key: str, fallback: str = '') -> str:
			return trans_mapping.get(key, key)

		template_dirs = [os.path.join(tranp_dir(), 'data/cpp/template')]
		env = {'immutable_param_types': ['std::string', 'std::vector', 'std::map', 'std::function']}
		setting = RendererSetting(template_dirs, translator, env)
		provider = renderer_helper_provider_cpp(setting)
		self.renderer = Renderer(setting, provider)

	def __load_trans_mapping(self, filepath: str) -> dict[str, str]:
		with open(filepath) as f:
			return cast(dict[str, str], yaml.safe_load(f))


class TestRenderer(TestCase):
	__fixture = Fixture()

	def assertRender(self, template: str, vars: dict[str, Any], expected: str) -> None:
		"""Note: 文字列の比較は通例と逆配置にした方が見やすいため逆で利用"""
		actual = self.__fixture.renderer.render(template, vars=vars)
		self.assertEqual(expected, actual)

	@data_provider([
		({'symbol': 'B', 'actual_type': 'A'}, 'using B = A;'),
	])
	def test_render_alt_class(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('alt_class', vars, expected)

	@data_provider([
		({'label': '', 'value': 1}, '1'),
		({'label': 'a', 'value': 1}, '1'),
	])
	def test_render_argument(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('argument', vars, expected)

	@data_provider([
		('move_assign', {'receiver': 'hoge', 'value': '1234'}, 'hoge = 1234;'),
		('move_assign_dict', {'receiver': 'hoge[0]', 'value': '1234'}, 'hoge[0] = 1234;'),
		('move_assign_declare', {'receiver': 'hoge', 'value': '1234', 'var_type': 'int'}, 'int hoge = 1234;'),
		('move_assign_declare', {'receiver': 'hoge', 'value': '1234', 'var_type': 'int', 'is_static': True}, 'static int hoge = 1234;'),
		('move_assign_declare', {'receiver': 'hoge', 'value': 'A(1)', 'var_type': 'A', 'is_initializer': True}, 'A hoge{1};'),
		('move_assign_destruction', {'receivers': ['hoge', 'fuga'], 'value': '{1234, 2345}'}, 'auto [hoge, fuga] = {1234, 2345};'),
		('anno_assign', {'receiver': 'hoge', 'value': '1234', 'var_type': 'int', 'annotation': ''}, 'int hoge = 1234;'),
		('anno_assign', {'receiver': 'hoge', 'var_type': 'int', 'value': '', 'annotation': ''}, 'int hoge;'),
		('anno_assign', {'receiver': 'hoge', 'value': 'A(1)', 'var_type': 'A', 'annotation': '', 'is_initializer': True}, 'A hoge{1};'),
		('anno_assign', {'receiver': 'm', 'var_type': 'std::map<int, int>', 'value': '{{0, 0}, {1, 10}}', 'annotation': 'Embed::static'}, 'static std::map<int, int> m = {{0, 0}, {1, 10}};'),
		('aug_assign', {'receiver': 'hoge', 'value': '1234', 'operator': '+='}, 'hoge += 1234;'),
	])
	def test_render_assign(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'assign/{template}', vars, expected)

	@data_provider([
		({'value_type': 'float', 'size': '10', 'default': '{100.0}', 'default_is_list': True}, 'std::vector<float>(10, 100.0)'),
		({'value_type': 'float', 'size': '10', 'default': 'std::vector<float>()', 'default_is_list': False}, 'std::vector<float>(10)'),
	])
	def test_render_binary_operator_fill_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator/fill_list', vars, expected)

	@data_provider([
		({'left': 'key', 'operator': 'in', 'right': 'items', 'right_is_dict': True}, 'items.contains(key)'),
		({'left': 'key', 'operator': 'not.in', 'right': 'items', 'right_is_dict': True}, '(!items.contains(key))'),
		({'left': 'value', 'operator': 'in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) != values.end())'),
		({'left': 'value', 'operator': 'not.in', 'right': 'values', 'right_is_dict': False}, '(std::find(values.begin(), values.end(), value) == values.end())'),
	])
	def test_render_binary_operator_in(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('binary_operator/in', vars, expected)

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
		self.assertRender('binary_operator/default', vars, expected)

	@data_provider([
		({'statements': [ 'int x = 0;', 'int y = 0;', 'int z = 0;', ]}, 'int x = 0;\nint y = 0;\nint z = 0;'),
	])
	def test_render_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('block', vars, expected)

	@data_provider([
		('default', {'type_name': 'Callable', 'parameters': ['int', 'float'], 'return_type': 'bool'}, 'std::function<bool(int, float)>'),
		('pluck_method', {'type_name': 'Callable', 'parameters': ['T', 'T_Args...'], 'return_type': 'void'}, 'typename PluckMethod<T, void, T_Args...>::method'),
	])
	def test_render_callable_type(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'callable_type/{template}', vars, expected)

	@data_provider([
		({'var_type': 'Exception', 'symbol': 'e', 'statements': ['pass;']}, '} catch (Exception e) {\n\tpass;'),
	])
	def test_render_catch(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('catch', vars, expected)

	@data_provider([
		({'accessor': 'public', 'decl_class_var': 'float a;'}, 'public: inline static float a;'),
	])
	def test_render_class_decl_class_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/_decl_class_var', vars, expected)

	@data_provider([
		({'accessor': 'public', 'decl_this_var': 'float a;', 'annotation': ''}, 'public: float a;'),
	])
	def test_render_class_decl_this_var(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/_decl_this_var', vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Hoge',
				'accessor': '',
				'decorators': ['deco(A, A.B)'],
				'inherits': ['Base', 'Interface'],
				'template_types': [],
				'comment': '',
				'statements': [
					'\n'.join([
						'private: int __value;',
						'private: std::string __text;',
						'public: Hoge() {',
						'	int hoge = 1234;',
						'	int fuga = 2345;',
						'}',
					]),
				],
				'module_path': 'module.path.to',
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
				'accessor': '',
				'decorators': [],
				'inherits': [],
				'template_types': [],
				'comment': '',
				'statements': [
					'\n'.join([
						'public: Hoge() {',
						'}',
					]),
				],
				'module_path': 'module.path.to',
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
				'accessor': '',
				'decorators': [],
				'inherits': [],
				'template_types': [],
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
				'module_path': 'module.path.to',
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
				'accessor': '',
				'decorators': ['deco(A, A.B)'],
				'inherits': [],
				'template_types': [],
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
				'module_path': 'module.path.to',
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
				'accessor': '',
				'decorators': [],
				'inherits': [],
				'template_types': [],
				'comment': '',
				'statements': [],
				'module_path': 'module.path.to',
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
		self.assertRender('class/class', vars, expected)

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
		self.assertRender(f'comp/{spec}', vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'is_const': False, 'is_addr_p': False}, 'auto& value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': True, 'is_addr_p': False}, 'const auto& value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': False, 'is_addr_p': True}, 'auto value : values'),
		({'symbols': ['value'], 'iterates': 'values', 'is_const': True, 'is_addr_p': True}, 'const auto value : values'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': False, 'is_addr_p': False}, 'auto& [key, value] : items'),
		({'symbols': ['key', 'value'], 'iterates': 'items', 'is_const': True, 'is_addr_p': False}, 'const auto& [key, value] : items'),
	])
	def test_render_comp_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('comp/comp_for', vars, expected)

	@data_provider([
		({'initializers': [], 'super_initializer': {}}, ''),
		({'initializers': [{'symbol': 'a', 'value': '1'}, {'symbol': 'b', 'value': '2'}], 'super_initializer': {}}, ' : a(1), b(2)'),
		({'initializers': [], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b)'),
		({'initializers': [{'symbol': 'a', 'value': '1'}], 'super_initializer': {'parent': 'A', 'arguments': 'a, b'}}, ' : A(a, b), a(1)'),
	])
	def test_render_constructor_initializer(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_initializer', vars, expected)

	@data_provider([
		({'path': 'deco', 'arguments': ['a', 'b']}, 'deco(a, b)'),
	])
	def test_render_decorator(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('decorator', vars, expected)

	@data_provider([
		({'targets': [{'receiver': 'l', 'key': '1', 'list_or_dict': 'list'}]}, 'l.erase(l.begin() + 1);'),
		({'targets': [{'receiver': 'd', 'key': '"a"', 'list_or_dict': 'dict'}]}, 'd.erase("a");'),
		({'targets': [{'receiver': 'l', 'key': '1', 'list_or_dict': 'list'}, {'receiver': 'd', 'key': '"a"', 'list_or_dict': 'dict'}]}, 'l.erase(l.begin() + 1);\nd.erase("a");'),
	])
	def test_render_delete(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'delete/default', vars, expected)

	@data_provider([
		({'key_type': 'int', 'value_type': 'float'}, 'std::map<int, float>'),
	])
	def test_render_dict_type(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('dict_type', vars, expected)

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
		self.assertRender('literal/doc_string', vars, expected)

	@data_provider([
		({'statements': ['int x = 0;'], 'meta_header': '@tranp.meta: {"version":"1.0.0"}', 'module_path': 'path.to'}, '// @tranp.meta: {"version":"1.0.0"}\n#pragma once\nint x = 0;\n'),
	])
	def test_render_entrypoint(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('entrypoint', vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Values',
				'accessor': '',
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
		(
			{
				'symbol': 'Values',
				'accessor': 'public',
				'decorators': [],
				'comment': '',
				'statements': [
					'int A = "a";',
					'int B = "b";',
				],
			},
			'\n'.join([
				'/** Values */',
				'public: enum class Values {',
				'	A,',
				'	B,',
				'};',
			]),
		),
	])
	def test_render_enum(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('class/enum', vars, expected)

	@data_provider([
		({'symbols': ['key', 'value'], 'iterates': 'items', 'statements': []}, 'for (auto& [key, value] : items) {\n}'),
	])
	def test_render_for_dict(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/dict', vars, expected)

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
		self.assertRender('for/enumerate', vars, expected)

	@data_provider([
		({'symbol': 'index', 'last_index': 'limit', 'statements': ['pass;']}, 'for (auto index = 0; index < limit; index++) {\n\tpass;\n}'),
	])
	def test_render_for_range(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/range', vars, expected)

	@data_provider([
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': False}, 'for (auto& value : values) {\n\tpass;\n}'),
		({'symbols': ['value'], 'iterates': 'values', 'statements': ['pass;'], 'is_const': True}, 'for (const auto& value : values) {\n\tpass;\n}'),
	])
	def test_render_for(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('for/default', vars, expected)

	@data_provider([
		({'arguments': ['"<string>"']}, '#include <string>'),
		({'arguments': ['"' '"path/to/module.h"' '"']}, '#include "path/to/module.h"'),
	])
	def test_render_func_call_c_include(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_include', vars, expected)

	@data_provider([
		({'arguments': ['"MACRO()"']}, 'MACRO()'),
	])
	def test_render_func_call_c_macro(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_macro', vars, expected)

	@data_provider([
		({'arguments': ['"once"']}, '#pragma once'),
	])
	def test_render_func_call_c_pragma(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/c_pragma', vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['1.0f'], 'is_statement': True}, 'static_cast<int>(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_bin_to_bin', vars, expected)

	@data_provider([
		({'arguments': ['1.0f'], 'is_statement': True}, 'std::to_string(1.0f);'),
	])
	def test_render_func_call_cast_bin_to_str(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_bin_to_str', vars, expected)

	@data_provider([
		({'arguments': ['"A"'], 'is_statement': True}, "'A';"),
		({'arguments': ['string[0]'], 'is_statement': True}, "string[0];"),
	])
	def test_render_func_call_cast_char(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_char', vars, expected)

	@data_provider([
		({'arguments': ['iterates'], 'is_statement': True}, 'iterates;'),
	])
	def test_render_func_call_cast_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_list', vars, expected)

	@data_provider([
		({'var_type': 'int', 'arguments': ['"1"'], 'is_statement': True}, 'std::stoi("1");'),
		({'var_type': 'int', 'arguments': ['"ff"', '16'], 'is_statement': True}, 'std::stoi("ff", 0, 16);'),
		({'var_type': 'float', 'arguments': ['"1.0"'], 'is_statement': True}, 'std::stod("1.0");'),
	])
	def test_render_func_call_cast_str_to_bin(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_str_to_bin', vars, expected)

	@data_provider([
		({'var_type': 'std::string', 'arguments': ['"1"'], 'is_statement': True}, 'std::string("1");'),
	])
	def test_render_func_call_cast_str_to_str(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cast_str_to_str', vars, expected)

	@data_provider([
		({'arguments': ['A(0)'], 'is_statement': True}, 'new A(0);'),
	])
	def test_render_func_call_cvar_new_p(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_p', vars, expected)

	@data_provider([
		({'var_type': 'std::vector<A>', 'initializer': '{0}, {1}', 'is_statement': True}, 'std::shared_ptr<std::vector<A>>(new std::vector<A>({0}, {1}));'),
	])
	def test_render_func_call_cvar_new_sp_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_sp_list', vars, expected)

	@data_provider([
		({'var_type': 'A', 'initializer': '0', 'is_statement': True}, 'std::make_shared<A>(0);'),
	])
	def test_render_func_call_cvar_new_sp(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_new_sp', vars, expected)

	@data_provider([
		({'var_type': 'int', 'is_statement': True}, 'std::shared_ptr<int>();'),
	])
	def test_render_func_call_cvar_sp_empty(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/cvar_sp_empty', vars, expected)

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
		self.assertRender('func_call/cvar_to', vars, expected)

	@data_provider([
		({'arguments': ['"s"', '-1'], 'receiver': 'items', 'operator': '.', 'is_statement': True}, 'items.contains("s") ? items["s"] : -1;'),
	])
	def test_render_func_call_dict_get(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/dict_get', vars, expected)

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
		self.assertRender('func_call/dict_keys', vars, expected)

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
		self.assertRender('func_call/dict_pop', vars, expected)

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
		self.assertRender('func_call/dict_values', vars, expected)

	@data_provider([
		({'calls': 'static_cast', 'arguments': ['Class*', 'p'], 'is_statement': True}, 'static_cast<Class*>(p);'),
	])
	def test_render_func_call_generic_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/generic_call', vars, expected)

	@data_provider([
		({'arguments': ['values'], 'is_statement': True}, 'values.size();'),
	])
	def test_render_func_call_len(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/len', vars, expected)

	@data_provider([
		({'receiver': 'values', 'operator': '.', 'arguments': ['1', 'value']}, 'values.insert(values.begin() + 1, value)'),
	])
	def test_render_func_call_list_insert(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/list_insert', vars, expected)

	@data_provider([
		({'receiver': 'values', 'operator': '.', 'arguments': ['values2']}, 'values.insert(values.end(), values2)'),
	])
	def test_render_func_call_list_extend(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/list_extend', vars, expected)

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
		self.assertRender('func_call/list_pop', vars, expected)

	@data_provider([
		({'arguments': ['"%d, %f"', '1', '1.0f'], 'is_statement': True}, 'printf("%d, %f", 1, 1.0f);'),
	])
	def test_render_func_call_print(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/print', vars, expected)

	@data_provider([
		({'calls': 'A.func', 'arguments': ['1 + 2', 'A.value']}, 'A.func(1 + 2, A.value)'),
	])
	def test_render_func_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call/default', vars, expected)

	@data_provider([
		({'statements': ['pass;']}, '{\n\tpass;\n}'),
	])
	def test_render_function_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_block', vars, expected)

	@data_provider([
		({'parameters': ['A self'], 'decorators': []}, ''),
		({'parameters': ['A self', 'bool b'], 'decorators': []}, 'bool b'),
		({'parameters': ['type<A> cls'], 'decorators': []}, ''),
		({'parameters': ['type<A> cls', 'bool b'], 'decorators': []}, 'bool b'),
		({'parameters': ['bool b', 'int n'], 'decorators': []}, 'bool b, int n'),
	])
	def test_render_function_definition_params(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('function/_definition_params', vars, expected)

	@data_provider([
		(
			'function',
			{
				'symbol': 'func',
				'decorators': ['deco(A, B)'],
				'parameters': ['const std::string& text', 'int value = 1'],
				'return_type': 'int',
				'comment': '',
				'statements': ['return value + 1;'],
				'template_types': ['T'],
				'is_pure': False,
			},
			'\n'.join([
				'/** func */',
				'template<typename T>',
				'int func(const std::string& text, int value = 1) {',
				'	return value + 1;',
				'}',
			]),
		),
		(
			'closure',
			{
				'symbol': 'closure',
				'decorators': [],
				'parameters': ['const std::string& text', 'int value = 1'],
				'return_type': 'int',
				# 'comment': '',
				'statements': ['return value + 1;'],
				# 'template_types': [],
				# 'is_pure': False,
				# closure only
			},
			'\n'.join([
				'auto closure = [&](const std::string& text, int value = 1) -> int {',
				'	return value + 1;',
				'};',
			]),
		),
		(
			'closure',
			{
				'symbol': 'closure_bind',
				'decorators': ['Embed.closure_bind(this, a, b)'],
				'parameters': ['const std::string& text', 'int value = 1'],
				'return_type': 'int',
				# 'comment': '',
				'statements': ['return value + 1;'],
				# 'template_types': [],
				# 'is_pure': False,
				# closure only
			},
			'\n'.join([
				'auto closure_bind = [this, a, b](const std::string& text, int value = 1) mutable -> int {',
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
				# 'is_pure': False,
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
				# 'is_pure': False,
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
				'is_pure': False,
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
				'is_pure': False,
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
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
				# method only
				'is_property': True,
			},
			'\n'.join([
				'public:',
				'/** method */',
				'inline void method(int value = 1) {',
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
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': True,
				'is_override': False,
				'allow_override': False,
				# method only
				'is_property': False,
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
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': True,
				# method only
				'is_property': False,
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
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': True,
				'allow_override': False,
				# method only
				'is_property': False,
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
				'template_types': ['T', 'T2', 'T_Args...'],
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
				# method only
				'is_property': False,
			},
			'\n'.join([
				'public:',
				'/** template_method */',
				'template<typename T, typename T2, typename ...T_Args>',
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
				'is_pure': True,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
				# method only
				'is_property': False,
			},
			'\n'.join([
				'private:',
				'/** decorated_method */',
				'void decorated_method(int value = 1) const {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'method',
			{
				'symbol': 'method_anno_returns',
				'decorators': [],
				'parameters': [],
				'return_type': 'std::string',
				'comment': '',
				'statements': ['return this->s;'],
				'template_types': [],
				'is_pure': False,
				# belongs class only
				'accessor': 'public',
				'class_symbol': 'Hoge',
				'is_abstract': False,
				'is_override': False,
				'allow_override': False,
				# method only
				'is_property': False,
				'return_type_annotation': 'Embed::immutable',
			},
			'\n'.join([
				'public:',
				'/** method_anno_returns */',
				'const std::string& method_anno_returns() {',
				'	return this->s;',
				'}',
			]),
		),
	])
	def test_render_function(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'function/{template}', vars, expected)

	@data_provider([
		('if', {'condition': 'value == 1', 'statements': ['pass;'], 'else_ifs': [], 'else_clause': ''}, 'if (value == 1) {\n\tpass;\n}'),
		('if', {'condition': 'value == 1', 'statements': ['pass;'], 'else_ifs': ['} else if (value == 2) {\n\tpass;'], 'else_clause': ''}, 'if (value == 1) {\n\tpass;\n} else if (value == 2) {\n\tpass;\n}'),
		('if', {'condition': 'value == 1', 'statements': ['pass;'], 'else_ifs': [], 'else_clause': '} else {\n\tpass;'}, 'if (value == 1) {\n\tpass;\n} else {\n\tpass;\n}'),
		('else_if', {'condition': 'value == 1', 'statements': ['pass;']}, '} else if (value == 1) {\n\tpass;'),
		('else_if', {'condition': 'std::is_same_v<T, int>', 'statements': ['pass;']}, '} else if constexpr (std::is_same_v<T, int>) {\n\tpass;'),
		('else', {'statements': ['pass;']}, '} else {\n\tpass;'),
	])
	def test_render_if_elif_else(self, spec: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'if/{spec}', vars, expected)

	@data_provider([
		({'module_path': 'module.path.to', 'import_dir': '', 'replace_dir': ''}, '// #include "module/path/to.h"'),
		({'module_path': 'module.path.to', 'import_dir': 'module/path/', 'replace_dir': 'path/'}, '#include "path/to.h"'),
	])
	def test_render_import(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('import', vars, expected)

	@data_provider([
		('class', {'var_type': 'int*'}, 'int*'),
		('class', {'var_type': 'int'}, 'int'),
		('cvar', {'receiver': 'p_arr', 'keys': ['0']}, '(*(p_arr))[0]'),
		('default', {'receiver': 'n', 'key': '0'}, 'n[0]'),
		('default', {'receiver': 'n', 'key': '0', 'is_statement': True}, 'n[0];'),
		('slice_string', {'receiver': 's', 'keys': ['0', '1']}, 's.substr(0, 1)'),
		('slice_string', {'receiver': 's', 'keys': ['1', '2']}, 's.substr(1, 2 - (1))'),
		('slice_string', {'receiver': 's', 'keys': ['1']}, 's.substr(1, s.size() - (1))'),
		('tuple', {'receiver': 't', 'key': '0'}, 'std::get<0>(t)'),
	])
	def test_render_indexer(self, spec: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'indexer/{spec}', vars, expected)

	@data_provider([
		({'expression': '1', 'var_type': 'int'}, '[&]() -> int { return 1; }'),
	])
	def test_render_lambda(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('lambda', vars, expected)

	@data_provider([
		('dict', {'items': ['{hoge, 1}','{fuga, 2}']}, '{\n\t{hoge, 1},\n\t{fuga, 2},\n}'),
		('dict', {'items': []}, '{}'),
		('falsy', {}, 'false'),
		('float', {'value': 1.0}, '1.0'),
		('integer', {'value': 1}, '1'),
		('list', {'values': ['1234', '2345']}, '{\n\t{1234},\n\t{2345},\n}'),
		('list', {'values': []}, '{}'),
		('null', {}, 'nullptr'),
		('pair', {'first': '"a"', 'second': '1'}, '{"a", 1}'),
		('string', {'value': "'a'"}, '"a"'),
		('string', {'value': '"a"'}, '"a"'),
		('truthy', {}, 'true'),
	])
	def test_render_literal(self, spec: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'literal/{spec}', vars, expected)

	@data_provider([
		# 明示変換系
		({'var_type': 'int', 'symbol': 'n', 'default_value': '', 'annotation': ''}, 'int n'),
		({'var_type': 'int', 'symbol': 'n', 'default_value': '', 'annotation': 'Embed::mutable'}, 'int n'),
		({'var_type': 'int', 'symbol': 'n', 'default_value': '', 'annotation': 'Embed::immutable'}, 'const int& n'),
		({'var_type': 'int', 'symbol': 'n', 'default_value': '1', 'annotation': ''}, 'int n = 1'),
		({'var_type': 'int', 'symbol': 'n', 'default_value': '1', 'annotation': 'Embed::mutable'}, 'int n = 1'),
		({'var_type': 'int', 'symbol': 'n', 'default_value': '1', 'annotation': 'Embed::immutable'}, 'const int& n = 1'),
		# 暗黙変換系
		({'var_type': 'std::string', 'symbol': 's', 'annotation': ''}, 'const std::string& s'),
		({'var_type': 'std::string', 'symbol': 's', 'annotation': 'Embed::mutable'}, 'std::string s'),
		({'var_type': 'std::string', 'symbol': 's', 'annotation': 'Embed::immutable'}, 'const std::string& s'),
		({'var_type': 'std::string*', 'symbol': 'p', 'annotation': ''}, 'const std::string* p'),
		({'var_type': 'std::string*', 'symbol': 'p', 'annotation': 'Embed::mutable'}, 'std::string* p'),
		({'var_type': 'std::string*', 'symbol': 'p', 'annotation': 'Embed::immutable'}, 'const std::string* p'),
		({'var_type': 'std::string&', 'symbol': 'p', 'annotation': ''}, 'const std::string& p'),
		({'var_type': 'std::string&', 'symbol': 'p', 'annotation': 'Embed::mutable'}, 'std::string& p'),
		({'var_type': 'std::string&', 'symbol': 'p', 'annotation': 'Embed::immutable'}, 'const std::string& p'),
		({'var_type': 'std::vector<int>', 'symbol': 'ns', 'annotation': ''}, 'const std::vector<int>& ns'),
		({'var_type': 'std::vector<int>', 'symbol': 'ns', 'annotation': 'Embed::mutable'}, 'std::vector<int> ns'),
		({'var_type': 'std::vector<int>', 'symbol': 'ns', 'annotation': 'Embed::immutable'}, 'const std::vector<int>& ns'),
		({'var_type': 'std::map<std::string, int>', 'symbol': 'dns', 'annotation': ''}, 'const std::map<std::string, int>& dns'),
		({'var_type': 'std::map<std::string, int>', 'symbol': 'dns', 'annotation': 'Embed::mutable'}, 'std::map<std::string, int> dns'),
		({'var_type': 'std::map<std::string, int>', 'symbol': 'dns', 'annotation': 'Embed::immutable'}, 'const std::map<std::string, int>& dns'),
		# 変換不可系
		({'var_type': 'const std::string', 'symbol': 'p', 'annotation': ''}, 'const std::string p'),
		({'var_type': 'const std::string', 'symbol': 'p', 'annotation': 'Embed::mutable'}, 'const std::string p'),
		({'var_type': 'const std::string', 'symbol': 'p', 'annotation': 'Embed::immutable'}, 'const std::string p'),
		({'var_type': 'const std::string&', 'symbol': 'p', 'annotation': ''}, 'const std::string& p'),
		({'var_type': 'const std::string&', 'symbol': 'p', 'annotation': 'Embed::mutable'}, 'const std::string& p'),
		({'var_type': 'const std::string&', 'symbol': 'p', 'annotation': 'Embed::immutable'}, 'const std::string& p'),
	])
	def test_render_parameter(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('parameter', vars, expected)

	@data_provider([
		({'receiver': 'raw', 'move': 'ToAddress'}, '(&(raw))'),
		({'receiver': 'addr', 'move': 'ToActual'}, '(*(addr))'),
		({'receiver': 'sp', 'move': 'UnpackSp'}, '(sp).get()'),
		({'receiver': 'raw', 'move': 'Copy'}, 'raw'),
	])
	def test_render_relay_cvar_to(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/cvar_to', vars, expected)

	@data_provider([
		({'receiver': 'a', 'operator': 'Raw', 'prop': 'b', 'is_property': False}, 'a.b'),
		({'receiver': 'a', 'operator': 'Raw', 'prop': 'b', 'is_property': True}, 'a.b()'),
		({'receiver': 'a', 'operator': 'Address', 'prop': 'b', 'is_property': False}, 'a->b'),
		({'receiver': 'a', 'operator': 'Address', 'prop': 'b', 'is_property': True}, 'a->b()'),
		({'receiver': 'A', 'operator': 'Static', 'prop': 'B', 'is_property': False}, 'A::B'),
	])
	def test_render_relay_default(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/default', vars, expected)

	@data_provider([
		# XXX `std::string`にならないのは不統一な印象を受ける
		({'prop': '__name__', 'var_type': 'str', 'literal': 'A'}, '"A"'),
		({'prop': '__module_path__', 'var_type': 'str', 'literal': 'module.path.to.A'}, '"module.path.to.A"'),
		({'prop': '__qualname__', 'var_type': 'str', 'literal': 'A.func'}, '"A.func"'),
		({'prop': 'E.value', 'var_type': 'int', 'literal': '1'}, '1'),
		({'prop': 'E.value', 'var_type': 'float', 'literal': '1.0'}, '1.0'),
		({'prop': 'E.value', 'var_type': 'str', 'literal': 'a'}, '"a"'),
	])
	def test_render_relay_literalize(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('relay/literalize', vars, expected)

	@data_provider([
		({'return_value': '(1 + 2)'}, 'return (1 + 2);'),
		({'return_value': ''}, 'return;'),
	])
	def test_render_return(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('return', vars, expected)

	@data_provider([
		({'condition': 'n == 1', 'assert_body': ''}, 'assert(n == 1);'),
		({'condition': 'a.ok', 'assert_body': 'std::exception'}, 'assert(a.ok); // std::exception'),
	])
	def test_render_assert(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('assert', vars, expected)

	@data_provider([
		({'throws': 'e', 'via': '', 'is_new': False}, 'throw e;'),
		({'throws': 'std::exception()', 'via': 'e', 'is_new': True}, 'throw new std::exception();'),
	])
	def test_render_throw(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('throw', vars, expected)

	@data_provider([
		({'statements': ['pass;'], 'catches': []}, 'try {\n\tpass;\n}'),
		({'statements': ['pass;'], 'catches': ['} catch (std::exception e) {\n\tthrow e;']}, 'try {\n\tpass;\n} catch (std::exception e) {\n\tthrow e;\n}'),
	])
	def test_render_try(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('try', vars, expected)

	@data_provider([
		('default', {'type_name': 'int'}, 'int'),
		('default', {'type_name': 'str'}, 'std::string'),
		('template', {'type_name': 'T', 'definition_type': 'TypeVar'}, 'T'),
		('template', {'type_name': 'T_Args', 'definition_type': 'TypeVarTuple'}, 'T_Args...'),
		('template', {'type_name': 'P', 'definition_type': 'ParamSpec'}, 'P'),
	])
	def test_render_var_of_type(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(f'var_of_type/{template}', vars, expected)
