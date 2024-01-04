import os
from typing import Any
from unittest import TestCase

from py2cpp.view.render import Renderer
from tests.test.helper import data_provider

class Fixture:
	@classmethod
	def appdir(cls) -> str:
		return os.path.join(os.path.dirname(__file__), '../../../..')

	@classmethod
	def renderer(cls) -> Renderer:
		return Renderer(os.path.join(cls.appdir(), 'example/template'))


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
		(
			{'values': ['1234', '2345']},
			'\n'.join([
				'{',
				'	{1234},',
				'	{2345},',
				'}',
			]),
		),
		({'values': []}, '{\n}'),
	])
	def test_render_list(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('list', 0, vars, expected)

	@data_provider([
		(
			{'items': [
				'{hoge, 1}',
				'{fuga, 2}',
			]},
			'\n'.join([
				'{',
				'	{hoge, 1},',
				'	{fuga, 2},',
				'}',
			]),
		),
		({'items': []}, '{\n}'),
	])
	def test_render_dict(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('dict', 0, vars, expected)

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
		({'module_path': 'module.path.to'}, '#include "module/path/to.h"'),
	])
	def test_render_import(self, vars: dict[str, Any], expected: str) -> None:
		self.assertRender('import', 0, vars, expected)

	@data_provider([
		(
			{
				'symbol': 'Hoge',
				'decorators': ['deco(A, A.B)'],
				'parents': ['Base', 'Interface'],
				'vars': [
					{'access': 'private', 'symbol': '__value', 'var_type': 'int'},
					{'access': 'private', 'symbol': '__text', 'var_type': 'string'},
				],
				'block': '\n'.join([
					'public: Hoge() {',
					'	int hoge = 1234;',
					'	int fuga = 2345;',
					'}',
				]),
			},
			'\n'.join([
				'deco(A, A.B)',
				'class Hoge : public Base, Interface {',
				'	private: int __value;',
				'	private: string __text;',
				'',
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
				'parents': [],
				'vars': [],
				'block': '\n'.join([
					'public: Hoge() {',
					'}',
				]),
			},
			'\n'.join([
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
				'block': '\n'.join([
					'A = 0;',
					'B = 1;',
				]),
			},
			'\n'.join([
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
				'parameters': ['string text', 'int value = 1'],
				'return_type': 'int',
				'block': 'return value + 1;',
			},
			'\n'.join([
				'deco(A, B)',
				'int func(string text, int value = 1) {',
				'	return value + 1;',
				'}',
			]),
		),
		(
			'constructor',
			{
				'access': 'public',
				'symbol': '__init__',
				'class_symbol': 'Hoge',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'block': 'this->x = value;',
			},
			'\n'.join([
				'public: Hoge(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
		(
			'class_method',
			{
				'access': 'public',
				'symbol': 'static_method',
				'class_symbol': 'Hoge',
				'decorators': [],
				'parameters': [],
				'return_type': 'int',
				'block': 'return 1;',
			},
			'\n'.join([
				'public: static int static_method() {',
				'	return 1;',
				'}',
			]),
		),
		(
			'method',
			{
				'access': 'public',
				'symbol': 'method',
				'class_symbol': 'Hoge',
				'decorators': [],
				'parameters': ['int value = 1'],
				'return_type': 'void',
				'block': 'this->x = value;',
			},
			'\n'.join([
				'public: void method(int value = 1) {',
				'	this->x = value;',
				'}',
			]),
		),
	])
	def test_render_function(self, template: str, vars: dict[str, Any], expected: str) -> None:
		self.assertRender(template, 0, vars, expected)
