from typing import Iterator, Protocol

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflection.base import IReflection


class SymbolDB:
	"""シンボルテーブル"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__items: dict[str, dict[str, IReflection]] = {}
		self.__preprocessed: dict[str, dict[str, bool]] = {}

	def __getitem__(self, key: str) -> IReflection:
		"""指定のキーのシンボルを取得

		Args:
			key (str): キー
		Returns:
			IReflection: シンボル
		Raises:
			KeyError: 存在しないキーを指定
		"""
		module_path, local_path = ModuleDSN.parsed(key)
		if module_path not in self.__items or local_path not in self.__items[module_path]:
			raise KeyError(f'Key not exists. key: {key}')

		return self.__items[module_path][local_path]

	def __setitem__(self, key: str, symbol: IReflection) -> None:
		"""指定のキーにシンボルを設定

		Args:
			key (str): キー
			symbol (IReflection): シンボル
		"""
		module_path, local_path = ModuleDSN.parsed(key)
		if module_path not in self.__items:
			self.__items[module_path] = {}

		self.__items[module_path][local_path] = symbol

	def __contains__(self, key: str) -> bool:
		"""指定のキーが存在するか判定

		Args:
			key (str): キー
		Returns:
			bool: True = 存在
		"""
		module_path, local_path = ModuleDSN.parsed(key)
		return module_path in self.__items and local_path in self.__items[module_path]

	def __len__(self) -> int:
		"""エントリーの総数を取得

		Returns:
			int: エントリーの総数
		"""
		total = 0
		for in_module in self.__items.values():
			total += len(in_module)

		return total

	def items(self) -> Iterator[tuple[str, IReflection]]:
		"""エントリーのイテレーターを取得

		Returns:
			Iterator[tuple[str, IReflection]]: イテレーター
		"""
		for module_path, in_module in self.__items.items():
			for local_path, value in in_module.items():
				yield ModuleDSN.full_joined(module_path, local_path), value

	def in_preprocess_items(self) -> Iterator[tuple[str, IReflection]]:
		"""プリプロセス中のシンボルのイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		Note:
			プリプロセッサー以外で使用するのは禁止
		"""
		for module_path, in_module in self.__items.items():
			for local_path, value in in_module.items():
				if module_path in self.__preprocessed and local_path in self.__preprocessed[module_path]:
					continue

				yield ModuleDSN.full_joined(module_path, local_path), value

	def keys(self) -> Iterator[str]:
		"""キーのイテレーターを取得

		Returns:
			Iterator[str]: イテレーター
		"""
		for module_path, in_module in self.__items.items():
			for local_path in in_module.keys():
				yield ModuleDSN.full_joined(module_path, local_path)

	def values(self) -> Iterator[IReflection]:
		"""シンボルのイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		for in_module in self.__items.values():
			for value in in_module.values():
				yield value

	def has_module(self, module_path: str) -> bool:
		"""モジュールが展開済みか判定

		Args:
			module_path (str): モジュールパス
		Returns:
			bool: True = 展開済み
		"""
		return module_path in self.__items

	def on_preprocess_complete(self, key: str) -> None:
		"""プリプロセス完了を記録

		Args:
			key (str): キー
		"""
		module_path, local_path = ModuleDSN.parsed(key)
		if module_path not in self.__preprocessed:
			self.__preprocessed[module_path] = {}

		self.__preprocessed[module_path][local_path] = True

	def unload(self, module_path: str) -> None:
		"""指定モジュール内のシンボルを削除

		Args:
			module_path (str): モジュールパス
		"""
		if module_path in self.__items:
			del self.__items[module_path]
			del self.__preprocessed[module_path]


class SymbolDBFinalizer(Protocol):
	"""シンボルテーブル完成プロセスプロトコル"""

	def __call__(self) -> SymbolDB:
		"""シンボルテーブル完成プロセスを実行"""
		...
