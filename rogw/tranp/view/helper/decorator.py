from collections.abc import Iterator, Sequence
import re

from rogw.tranp.lang.annotation import implements
from rogw.tranp.view.helper.block import BlockParser


class DecoratorHelper:
	"""デコレーターヘルパー"""

	def __init__(self, decorator: str) -> None:
		"""インスタンスを生成

		Args:
			decorator: デコレーター
		"""
		self.decorator: str = decorator
		self._props: tuple[str, dict[str, str], str] = ('', {}, '')

	def _parse(self, decorator: str) -> tuple[str, dict[str, str], str]:
		"""デコレーターを解析

		Args:
			decorator: デコレーター
		Returns:
			(パス, 引数一覧, 分解前の引数一覧)
		"""
		args_begin = decorator.find('(')
		path = decorator[:args_begin]

		join_args = decorator[args_begin + 1:len(decorator) - 1]
		args: dict[str, str] = {}
		for index, arg in enumerate(BlockParser.break_separator(join_args, ',')):
			if arg.count('=') > 0:
				label, *remain = arg.split('=')
				args[label] = '='.join(remain)
			else:
				args[str(index)] = arg

		return path, args, join_args
	
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
	def join_args(self) -> str:
		"""str: 引数一覧"""
		if len(self._props[0]) == 0:
			self._props = self._parse(self.decorator)

		return self._props[2]

	@property
	def arg(self) -> str:
		"""str: 第1引数の値"""
		return list(self.args.values())[0]

	def arg_at(self, index: int) -> str:
		"""指定のインデックスの引数の値を取得

		Args:
			index: インデックス
		Returns:
			引数の値
		"""
		values = list(self.args.values())
		return values[index]

	def arg_by(self, key: str) -> str:
		"""指定のキーの引数の値を取得

		Args:
			key: キー
		Returns:
			引数の値
		"""
		return self.args[key]

	def any(self, *paths: str) -> bool:
		"""指定のパスと一致するか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
		Returns:
			True = 含む
		"""
		return self.path in paths

	def match(self, pattern: str) -> bool:
		"""指定のパターンと一致するか判定

		Args:
			pattern: 正規表現
		Returns:
			True = 条件に合致
		"""
		return re.search(pattern, self.decorator) != None

	def any_args(self, subject: str) -> bool:
		"""引数が指定の条件と一致するか判定

		Args:
			subject: 検索条件
		Returns:
			True = 含む
		"""
		return self.join_args.find(subject) != -1

	def match_args(self, pattern: str) -> bool:
		"""引数が指定のパターンと一致するか判定

		Args:
			pattern: 正規表現
		Returns:
			True = 条件に合致
		"""
		return re.search(pattern, self.join_args) != None


class DecoratorQuery(Sequence):
	"""デコレータークエリー"""

	@classmethod
	def parse(cls, decorators: list[str]) -> 'DecoratorQuery':
		"""インスタンスを生成

		Args:
			decorators: デコレーターリスト
		Returns:
			インスタンス
		"""
		return cls([DecoratorHelper(decorator) for decorator in decorators])

	def __init__(self, helpers: list[DecoratorHelper]) -> None:
		"""インスタンスを生成

		Args:
			helpers: デコレーターヘルパーリスト
		"""
		self._helpers = helpers

	@implements
	def __iter__(self) -> Iterator[DecoratorHelper]:
		"""イテレーターを生成

		Returns:
			イテレーター
		"""
		for helper in self._helpers:
			yield helper

	@implements
	def __len__(self) -> int:
		"""要素数を取得

		Returns:
			要素数
		"""
		return len(self._helpers)

	@implements
	def __getitem__(self, index: int) -> DecoratorHelper:
		"""指定のインデックスの要素を取得

		Args:
			index: インデックス
		Returns:
			デコレーターヘルパー
		"""
		return self._helpers[index]

	def any(self, *path: str) -> 'DecoratorQuery':
		"""指定のパスと一致する要素を抽出し、新たにインスタンスを生成

		Args:
			*paths (str): 対象のデコレーターパスリスト
		Returns:
			インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.any(*path)])

	def match(self, pattern: str) -> 'DecoratorQuery':
		"""指定のパターンと一致する要素を抽出し、新たにインスタンスを生成

		Args:
			pattern: 正規表現
		Returns:
			インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.match(pattern)])

	def any_args(self, subject: str) -> 'DecoratorQuery':
		"""引数が指定の条件と一致する要素を抽出し、新たにインスタンスを生成

		Args:
			subject: 検索条件
		Returns:
			インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.any_args(subject)])

	def match_args(self, pattern: str) -> 'DecoratorQuery':
		"""引数が指定のパターンと一致する要素を抽出し、新たにインスタンスを生成

		Args:
			pattern: 正規表現
		Returns:
			インスタンス
		"""
		return self.__class__([helper for helper in self._helpers if helper.match_args(pattern)])

	def contains(self, *path: str) -> bool:
		"""指定のパスを持つ要素を含むか判定

		Args:
			*paths (str): 対象のデコレーターパスリスト
		Returns:
			True = 条件に合致
		"""
		for helper in self._helpers:
			if helper.any(*path):
				return True

		return False
