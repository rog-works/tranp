from collections.abc import Iterator, Sequence
import re

from rogw.tranp.lang.annotation import implements
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

	def matched(self, pattern: str) -> bool:
		"""指定のスキームと一致するか判定(正規表現)

		Args:
			pattern (str): 正規表現
		Returns:
			bool: True = 条件に合致
		"""
		return re.search(pattern, self.decorator) != None


class DecoratorQuery(Sequence):
	"""デコレータークエリー"""

	@classmethod
	def parse(cls, decorators: list[str]) -> 'DecoratorQuery':
		"""インスタンスを生成

		Args:
			decorators (list[str]): デコレーターリスト
		Returns:
			DecoratorQuery: インスタンス
		"""
		return cls([DecoratorHelper(decorator) for decorator in decorators])

	def __init__(self, helpers: list[DecoratorHelper]) -> None:
		"""インスタンスを生成

		Args:
			helpers (list[DecoratorHelper]): デコレーターヘルパーリスト
		"""
		self._helpers = helpers

	@implements
	def __iter__(self) -> Iterator[DecoratorHelper]:
		"""イテレーターを生成

		Returns:
			Iterator[DecoratorHelper]: イテレーター
		"""
		for helper in self._helpers:
			yield helper

	@implements
	def __len__(self) -> int:
		"""要素数を取得

		Returns:
			int: 要素数
		"""
		return len(self._helpers)

	@implements
	def __getitem__(self, index: int) -> DecoratorHelper:
		"""指定のインデックスの要素を取得

		Args:
			index (int): インデックス
		Returns:
			DecoratorHelper: デコレーターヘルパー
		"""
		return self._helpers[index]

	def filter(self, *path: str, **args: str) -> 'DecoratorQuery':
		"""指定のスキームと一致する要素を抽出し、新たにインスタンスを生成

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			DecoratorQuery: インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.any(*path, **args)])

	def match(self, pattern: str) -> 'DecoratorQuery':
		"""指定のパターンと一致する要素を抽出し、新たにインスタンスを生成

		Args:
			pattern (str): 正規表現
		Returns:
			DecoratorQuery: インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.matched(pattern)])

	def contains(self, *path: str, **args: str) -> bool:
		"""指定のスキームを持つ要素を含むか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
			**args (str): 引数リストの条件一覧
		Returns:
			bool: True = 条件に合致
		"""
		for helper in self._helpers:
			if helper.any(*path, **args):
				return True

		return False
