from typing import Any
from unittest import TestCase

from rogw.tranp.implements.cpp.view.cpp_view_helper import CppViewHelper
from rogw.tranp.test.helper import data_provider


class TestCppViewHelper(TestCase):
	@data_provider([
		('int n', {'var_type': 'int', 'symbol': 'n', 'default_value': '', 'var_type_origin': 'int'}),
		('int n = 0', {'var_type': 'int', 'symbol': 'n', 'default_value': '0', 'var_type_origin': 'int'}),
		('std::string s = ""', {'var_type': 'std::string', 'symbol': 's', 'default_value': '""', 'var_type_origin': 'std::string'}),
		('std::vector<int> ns = {1}', {'var_type': 'std::vector<int>', 'symbol': 'ns', 'default_value': '{1}', 'var_type_origin': 'std::vector'}),
		('std::map<std::string, int> dns = {{"a", 1}}', {'var_type': 'std::map<std::string, int>', 'symbol': 'dns', 'default_value': '{{"a", 1}}', 'var_type_origin': 'std::map'}),
		('const std::map<std::string, int>& dns', {'var_type': 'const std::map<std::string, int>&', 'symbol': 'dns', 'default_value': '', 'var_type_origin': 'std::map'}),
		('const int n', {'var_type': 'const int', 'symbol': 'n', 'default_value': '', 'var_type_origin': 'int'}),
		('int& n', {'var_type': 'int&', 'symbol': 'n', 'default_value': '', 'var_type_origin': 'int'}),
	])
	def test_param_parse(self, parameter: str, expected: dict[str, Any]) -> None:
		instance = CppViewHelper.Param.parse(parameter)
		self.assertEqual(expected['var_type'], instance.var_type)
		self.assertEqual(expected['symbol'], instance.symbol)
		self.assertEqual(expected['default_value'], instance.default_value)
		self.assertEqual(expected['var_type_origin'], instance.var_type_origin)

	@data_provider([
		('std::string', [], 'const std::string&'),
		('std::string*', [], 'const std::string*'),
		('std::string', [CppViewHelper.VarType.AnnoMutable], 'std::string'),
		('std::string*', [CppViewHelper.VarType.AnnoMutable], 'std::string*'),
		('std::string&', [CppViewHelper.VarType.AnnoMutable], 'std::string&'),
		('int', [], 'int'),
		('int*', [], 'int*'),
		('int&', [], 'int&'),
		('int', [CppViewHelper.VarType.AnnoImmutable], 'const int&'),
		('int*', [CppViewHelper.VarType.AnnoImmutable], 'const int*'),
		('int&', [CppViewHelper.VarType.AnnoImmutable], 'const int&'),
	])
	def test_var_type_annotated(self, var_type: str, annotations: list[str], expected: str) -> None:
		# @see example/config.yml
		immutable_param_types = ['std::string', 'std::vector', 'std::map', 'std::function']
		actual = CppViewHelper.VarType.annotated(var_type, annotations, immutable_param_types)
		self.assertEqual(expected, actual)
