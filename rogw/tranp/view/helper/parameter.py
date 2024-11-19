import re
from typing import cast

from rogw.tranp.view.helper.block import BlockParser


class ParameterHelper:
	"""パラメーターヘルパー

	Note:
		### 期待値
		1. `int n`
		2. `int n = 0`
		3. `int* p`
		4. `int* p = nullptr`
		5. `const int& n`
		XXX C++のシグネシャーを前提とする点に注意
	"""

	@classmethod
	def parse(cls, parameter: str) -> 'ParameterHelper':
		"""パラメーターを元にインスタンスを生成

		Args:
			parameter (str): パラメーター
		Returns:
			ParameterHelper: インスタンス
		"""
		param_default = BlockParser.break_separator(parameter, '=')
		param, default_value = param_default if len(param_default) == 2 else (param_default[0], '')
		type_symbol = BlockParser.break_separator(param, ' ')
		symbol = type_symbol.pop()
		var_type = ' '.join(type_symbol)
		return cls(var_type, symbol, default_value)

	def __init__(self, var_type: str, symbol: str, default_value: str) -> None:
		"""インスタンスを生成

		Args:
			var_type (str): 型
			symbol (str): シンボル名
			default_value (str): デフォルト値
		"""
		self.var_type = var_type
		self.symbol = symbol
		self.default_value = default_value

	@property
	def var_type_origin(self) -> str:
		"""Returns: str: ベースの型"""
		if self.var_type.startswith('const') or self.var_type[-1] in ['*', '&']:
			return cast(re.Match, re.search(r'^(const\s+)?([\w\d\:]+)[^\*&]*[\*&]?', self.var_type))[2]
		else:
			return self.var_type.split('<')[0]
