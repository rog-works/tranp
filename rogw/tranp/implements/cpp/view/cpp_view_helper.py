import re
from collections.abc import Callable
from typing import ClassVar, cast

from rogw.tranp.lang.convertion import as_a
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.render import RendererHelperFactory, RendererSetting


class CppViewHelper:
	"""ビューヘルパー(C++用)"""

	class SuperInitializer:
		"""ヘルパー(C++/イニシャライザー/スーパーコール)"""

		SuperCall: ClassVar = re.compile(r'([\w\d]+)::__init__\(([^;]*)\);$')

		@classmethod
		def parse(cls, statement: str) -> tuple[str, str]:
			"""Args: stetement: ステートメント Returns: (親クラス名, コンストラクター引数)"""
			return as_a(re.Match, re.search(cls.SuperCall, statement)).group(1, 2)

	class Initializer:
		"""ヘルパー(C++/イニシャライザー/メンバー初期化)"""

		MoveAssign: ClassVar = re.compile(r'.+\s+this->([\w\d]+)\s+=\s+([^;]+);')
		Initializer: ClassVar = re.compile(r'.+\s+this->([\w\d]+)(\{[^;]*\});')
		Empty: ClassVar = re.compile(r'.+\s+this->([\w\d]+);')

		@classmethod
		def parse(cls, statement: str) -> tuple[str, str]:
			"""Args: stetement: ステートメント Returns: (シンボル名, 初期化子)"""
			matches = as_a(re.Match, re.fullmatch(cls.MoveAssign, statement) or re.fullmatch(cls.Initializer, statement) or re.fullmatch(cls.Empty, statement)).groups()
			return matches[0], (matches[1] if len(matches) == 2 else '')

	class Param:
		"""ヘルパー(C++/パラメーター)"""

		@classmethod
		def parse(cls, parameter: str) -> 'CppViewHelper.Param':
			"""Args: parameter: パラメーター Returns: インスタンス

			Note:
				```
				### 期待値
				1. `int n`
				2. `int n = 0`
				3. `int* p`
				4. `int* p = nullptr`
				5. `const int& n`
				```
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
				var_type: 型
				symbol: シンボル名
				default_value: デフォルト値
			"""
			self.var_type = var_type
			self.symbol = symbol
			self.default_value = default_value

		@property
		def var_type_origin(self) -> str:
			"""Returns: ベースの型"""
			if self.var_type.startswith('const') or self.var_type[-1] in ['*', '&']:
				return cast(re.Match, re.search(r'^(const\s+)?([\w\d\:]+)[^\*&]*[\*&]?', self.var_type))[2]
			else:
				return self.var_type.split('<')[0]

	class Method:
		"""ヘルパー(C++/メソッド)"""

		PatternFor: ClassVar = re.compile(r'for \([^;]+; [\w\d]+ < this->([\w\d]+)([^;]+); [^)]+\) \{')
		PatternYield: ClassVar = re.compile(r'\s+return this->[\w\d]+\[[^;]+\]([^;]*);')

		@classmethod
		def break_iterator_list_complex(cls, statements: list[str]) -> tuple[int, str, str, str]:
			"""イテレーターメソッドのステートメントを分解

			Args:
				statements: ステートメントリスト
			Returns:
				(ステートメント終了位置, イテレーション要素, サイズ取得, 値取得)
			Note:
				### 期待値
				```cpp
				Iterator<std::string> keys() {
					for (auto index = 0; index < this->__entries.size(); index += 1) {
						return this->__entries[index].key();
					}
				}
			"""
			for_index = [index for index, statement in enumerate(statements) if statement.startswith('for ')][0]
			for_statements = statements[for_index].split('\n')
			matches_for = as_a(re.Match, cls.PatternFor.fullmatch(for_statements[0]))
			matches_yield = as_a(re.Match, cls.PatternYield.fullmatch(for_statements[1]))
			iterates, get_size = matches_for.group(1, 2)
			get_value = matches_yield.group(1)
			return for_index, iterates, get_size, get_value


def super_initializer_parse(setting: RendererSetting) -> Callable[[str], tuple[str, str]]:
	"""Note: @see rogw.tranp.implements.cpp.view.cpp_view_helper.CppViewHelper.SuperInitializer.parse"""
	return lambda statement: CppViewHelper.SuperInitializer.parse(statement)


def initializer_parse(setting: RendererSetting) -> Callable[[str], tuple[str, str]]:
	"""Note: @see rogw.tranp.implements.cpp.view.cpp_view_helper.CppViewHelper.Initializer.parse"""
	return lambda statement: CppViewHelper.Initializer.parse(statement)


def parameter_parse(setting: RendererSetting) -> Callable[[str], CppViewHelper.Param]:
	"""Note: @see rogw.tranp.implements.cpp.view.cpp_view_helper.CppViewHelper.Param.parse"""
	return lambda parameter: CppViewHelper.Param.parse(parameter)


def break_iterator_list_complex(setting: RendererSetting) -> Callable[[list[str]], tuple[int, str, str, str]]:
	"""Note: @see rogw.tranp.implements.cpp.view.cpp_view_helper.CppViewHelper.Method.break_iterator_list_complex"""
	return lambda statements: CppViewHelper.Method.break_iterator_list_complex(statements)


def factories_for_cpp() -> tuple[list[RendererHelperFactory], list[RendererHelperFactory]]:
	"""Returns: (ヘルパー一覧, フィルター一覧)"""
	return ([super_initializer_parse, initializer_parse, parameter_parse, break_iterator_list_complex], [])
