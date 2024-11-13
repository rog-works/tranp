from collections.abc import Iterator, MutableMapping
from typing import KeysView, ValuesView

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.serialization import DictSerialized, IReflectionSerializer


class SymbolDB(MutableMapping[str, IReflection]):
	"""シンボルテーブル"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__paths: dict[str, tuple[str, str]] = {}
		self.__items: dict[str, IReflection] = {}
		self.__completed: list[str] = []

	def __getitem__(self, key: str) -> IReflection:
		"""指定のキーのシンボルを取得

		Args:
			key (str): キー
		Returns:
			IReflection: シンボル
		Raises:
			KeyError: 存在しないキーを指定
		"""
		if key in self.__items:
			return self.__items[key]

		raise KeyError(f'Key not exists. key: {key}')

	def __setitem__(self, key: str, symbol: IReflection) -> None:
		"""指定のキーにシンボルを設定

		Args:
			key (str): キー
			symbol (IReflection): シンボル
		"""
		if key not in self.__items:
			self.__paths[key] = ModuleDSN.parsed(key)

		self.__items[key] = symbol

	def __delitem__(self, key: str) -> None:
		"""指定のキーのシンボルを削除

		Args:
			key (str): キー
		Raises:
			NotImplementedError: 非対応
		"""
		raise NotImplementedError(f'Operation not allowed. key: {key}')
	
	def __iter__(self) -> Iterator[str]:
		"""キーのイテレーターを取得

		Returns:
			Iterator[str]: イテレーター
		"""
		for key in self.keys():
			yield key

	def __contains__(self, key: str) -> bool:
		"""指定のキーが存在するか判定

		Args:
			key (str): キー
		Returns:
			bool: True = 存在
		"""
		return key in self.__items

	def __len__(self) -> int:
		"""エントリーの総数を取得

		Returns:
			int: エントリーの総数
		"""
		return len(self.__items)

	def items(self, for_module_path: str | None = None) -> Iterator[tuple[str, IReflection]]:
		"""エントリーのイテレーターを取得

		Args:
			for_module_path (str | None): 取得対象のモジュールパス (default = None)
		Returns:
			Iterator[tuple[str, IReflection]]: イテレーター
		"""
		if not for_module_path:
			return self.__items.values()

		for key, paths in self.__paths.items():
			if paths[0] == for_module_path:
				yield key, self.__items[key]

	def keys(self) -> KeysView[str]:
		"""キーのジェネレーターを取得

		Returns:
			KeysView[str]: ジェネレーター
		"""
		return self.__items.keys()

	def values(self) -> ValuesView[IReflection]:
		"""シンボルのジェネレーターを取得

		Returns:
			ValuesView[IReflection]: ジェネレーター
		"""
		return self.__items.values()

	def has_module(self, module_path: str) -> bool:
		"""モジュールが展開済みか判定

		Args:
			module_path (str): モジュールパス
		Returns:
			bool: True = 展開済み
		"""
		module_paths = [module_path for module_path, _ in self.__paths.values()]
		return module_path in module_paths

	def completed(self, module_path: str) -> bool:
		"""モジュールがプリプロセス完了済みか判定

		Args:
			module_path (str): モジュールパス
		Returns:
			bool: True = 完了済み
		"""
		return module_path in self.__completed

	def on_complete(self, module_path: str) -> None:
		"""モジュールのプリプロセス完了を記録

		Args:
			module_path (str): モジュールパス
		"""
		if module_path not in self.__completed:
			self.__completed.append(module_path)

	def unload(self, module_path: str) -> None:
		"""指定モジュール内のシンボルを削除

		Args:
			module_path (str): モジュールパス
		"""
		if module_path in self.__completed:
			self.__completed.remove(module_path)

		for key in self.__items.keys():
			if self.__paths[key][0] == module_path:
				del self.__items[key]

	def to_json(self, serializer: IReflectionSerializer, for_module_path: str | None = None) -> dict[str, DictSerialized]:
		"""JSONデータとして内部データをシリアライズ

		Args:
			serializer (IReflectionSerializer): シンボルシリアライザー
			for_module_path (str | None): 出力モジュールパス (default = None)
		Returns:
			dict[str, DictSerialized]: JSONデータ
		"""
		return {key: serializer.serialize(self[key]) for key in self._order_keys(for_module_path)}

	def import_json(self, serializer: IReflectionSerializer, data: dict[str, DictSerialized]) -> None:
		"""JSONデータを基に内部データをデシリアライズ。既存データを残したまま追加

		Args:
			serializer (IReflectionSerializer): シンボルシリアライザー
			data (dict[str, DictSerialized]): JSONデータ
		"""
		for key, row in data.items():
			self[key] = serializer.deserialize(self, row)
			module_path = ModuleDSN.parsed(key)[0]
			if not self.completed(module_path):
				self.on_complete(module_path)

	def _order_keys(self, for_module_path: str | None) -> list[str]:
		"""参照順にキーの一覧を取得

		Args:
			for_module_path (str | None): 出力モジュールパス
		Returns:
			list[str]: キーリスト
		"""
		orders: list[str] = []
		for key, paths in self.__paths.items():
			module_path = paths[0]
			if for_module_path is None or module_path == for_module_path:
				self._order_keys_recursive(module_path, self.__items[key], orders)
				if key not in orders:
					orders.append(key)

		return orders

	def _order_keys_recursive(self, for_module_path: str | None, symbol: IReflection, orders: list[str]) -> None:
		"""参照順にキーの一覧を更新

		Args:
			for_module_path (str | None): 出力モジュールパス
			symbol (IReflection): シンボル
			orders (list[str]): キーリスト
		Returns:
			list[str]: キーリスト
		"""
		for attr in symbol.attrs:
			self._order_keys_recursive(for_module_path, attr, orders)

		if not for_module_path or for_module_path == symbol.types.module_path and symbol.types.fullyname not in orders:
			orders.append(symbol.types.fullyname)
