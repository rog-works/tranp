from collections.abc import Iterator
import re

from rogw.tranp.lang.parser import BlockParser


class DecoratorHelper:
	"""デコレーターヘルパー"""

	def __init__(self, decorator: str) -> None:
		"""インスタンスを生成

		Args:
			decorator (str): デコレーター
		"""
		self.decorator: str = decorator
		self._props: tuple[str, dict[str, str]] = ('', {})

	def _parse(self, decorator: str) -> tuple[str, dict[str, str]]:
		"""デコレーターを解析

		Args:
			decorator (str): デコレーター
		Returns:
			tuple[str, dict[str, str]]: (パス, 引数一覧)
		"""
		param_begin = decorator.find('(')
		join_params = decorator[param_begin + 1:len(decorator) - 1]
		params: dict[str, str] = {}
		for index, param_block in enumerate(BlockParser.break_separator(join_params, ',')):
			if param_block.count('=') > 0:
				label, *remain = param_block.split('=')
				params[label] = '='.join(remain)
			else:
				params[str(index)] = param_block

		param_begin = decorator.find('(')
		path = decorator[:param_begin]
		return path, params
	
	@property
	def path(self) -> str:
		"""str: デコレーターパス"""
		if len(self._props[0]) == 0:
			self._props = self._parse(self.decorator)

		return self._props[0]

	@property
	def args(self) -> dict[str, str]:
		"""dict[str, str]: 引数一覧"""
		if len(self._props[0]) == 0:
			self._props = self._parse(self.decorator)

		return self._props[1]

	@property
	def arg(self) -> str:
		"""str: 第1引数の値"""
		return list(self.args.values())[0]

	def arg_at(self, index: int) -> str:
		"""指定のインデックスの引数の値を取得

		Args:
			index (int): インデックス
		Returns:
			str: 引数の値
		"""
		values = list(self.args.values())
		return values[index]

	def arg_by(self, key: str) -> str:
		"""指定のキーの引数の値を取得

		Args:
			key (str): キー
		Returns:
			str: 引数の値
		"""
		return self.args[key]

	def any(self, *paths: str, **args: str) -> bool:
		"""指定のスキームと一致するか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			bool: True = 条件に合致
		"""
		if self.path not in paths:
			return False

		for label, condition in args.items():
			if label not in self.args:
				return False

			if self.args[label] != condition:
				return False

		return True

	def match(self, pattern: str) -> bool:
		"""指定のスキームと一致するか判定(正規表現)

		Args:
			pattern (str): 正規表現
		Returns:
			bool: True = 条件に合致
		"""
		return re.search(pattern, self.decorator) != None


class DecoratorQuery:
	"""デコレータークエリー"""

	def __init__(self, decorators: list[str]) -> None:
		"""インスタンスを生成

		Args:
			decorators (list[str]): デコレーターリスト
		"""
		self.helpers = [DecoratorHelper(decorator) for decorator in decorators]

	def __iter__(self) -> Iterator[DecoratorHelper]:
		"""イテレーターを生成

		Returns:
			Iterator[DecoratorHelper]: イテレーター
		"""
		for helper in self.helpers:
			yield helper

	def filter(self, *path: str, **args: str) -> list[DecoratorHelper]:
		"""指定のスキームと一致する要素を返却

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			list[DecoratorHelper]: デコレーターヘルパーリスト
		"""
		return [helper for helper in self.helpers if helper.any(*path, **args)]

	def any(self, *path: str, **args: str) -> bool:
		"""指定のスキームと一致するか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			bool: True = 条件に合致
		"""
		for helper in self.helpers:
			if helper.any(*path, **args):
				return True

		return False

	def match(self, pattern: str) -> bool:
		"""指定のスキームと一致するか判定(正規表現)

		Args:
			pattern (str): 正規表現
		Returns:
			bool: True = 条件に合致
		"""
		for helper in self.helpers:
			if helper.match(pattern):
				return True

		return False
