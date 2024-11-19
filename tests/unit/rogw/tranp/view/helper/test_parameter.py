from typing import Any
from unittest import TestCase

from rogw.tranp.test.helper import data_provider
from rogw.tranp.view.helper.parameter import ParameterHelper


class TestParameterHelper(TestCase):
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
	def test_schema(self, parameter: str, expected: dict[str, Any]) -> None:
		instance = ParameterHelper.parse(parameter)
		self.assertEqual(instance.var_type, expected['var_type'])
		self.assertEqual(instance.symbol, expected['symbol'])
		self.assertEqual(instance.default_value, expected['default_value'])
		self.assertEqual(instance.var_type_origin, expected['var_type_origin'])
