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
			to_classes_alias('dict.append'): 'emplace',
			to_classes_alias('dict'): 'std::map',
			to_classes_alias('list'): 'std::vector',
			to_classes_alias('str'): 'std::string',
			to_cpp_alias('vector.begin'): 'begin',
			to_cpp_alias('vector.end'): 'end',
		}
		def translator(key: str) -> str:
			return trans_mapping.get(key, key)

		return Renderer(os.path.join(tranp_dir(), 'data/cpp/template'), translator)


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
		(
			{
				'statements': [
					'int x = 0;',
					'int y = 0;',
					'int z = 0;',
				],
			},
			'\n'.join([
				'int x = 0;',
				'int y = 0;',
				'int z = 0;',
			]),
		),
	])
	def test_render_block(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('block', 0, vars, expected)

	@data_provider([
		({'var_type': 'Exception', 'symbol': 'e', 'block': 'pass'}, 'catch (Exception e) {\n\tpass\n}'),
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
		({'symbols': ['value'], 'iterates': 'values'}, 'auto& value : values'),
		({'symbols': ['key', 'value'], 'iterates': 'items'}, 'auto& [key, value] : items'),
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
				'projection': '{key, {value}}',
				'comp_for': 'auto& [key, value] : items',
				'condition': '',
				'projection_types': ['int', 'float'],
				'binded_this': False,
			},
			'\n'.join([
				'[&]() -> std::map<int, float> {',
				'	std::map<int, float> __ret;',
				'	for (auto& [key, value] : items) {',
				'		__ret.emplace({key, {value}});',
				'	}',
				'	return __ret;',
				'}()',
			]),
		),
		(
			{
				'projection': '{key, {value}}',
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
				'			__ret.emplace({key, {value}});',
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
		({'values': ['1234', '2345']},'{\n\t{1234},\n\t{2345},\n}'),
		({'values': []}, '{}'),
	])
	def test_render_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('list', 0, vars, expected)

	@data_provider([
		({'calls': 'A.func', 'arguments': ['1 + 2', 'A.value']}, 'A.func(1 + 2, A.value)'),
	])
	def test_render_func_call(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('func_call', 0, vars, expected)

	@data_provider([
		({'return_value': '(1 + 2)'}, 'return (1 + 2);'),
	])
	def test_render_return(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('return', 0, vars, expected)

	@data_provider([
		({'module_path': 'module.path.to'}, '// #include "module/path/to.h"'),
	])
	def test_render_import(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('import', 0, vars, expected)

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
		(
			'function',
			{
				'symbol': 'func',
				'decorators': ['deco(A, B)'],
				'parameters': ['std::string text', 'int value = 1'],
				'return_type': 'int',
				'comment': '',
				'statements': ['return value + 1;'],
				'template_types': [],
			},
			'\n'.join([
				'/** func */',
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
				'}',
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
