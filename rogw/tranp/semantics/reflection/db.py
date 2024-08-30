from typing import Iterator, MutableMapping, Protocol

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.serialization import DictSerialized, IReflectionSerializer


class SymbolDB(MutableMapping[str, IReflection]):
	"""シンボルテーブル"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__items: dict[str, dict[str, IReflection]] = {}
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
		for module_path, in_modules in self.__items.items():
			for local_path in in_modules.keys():
				yield ModuleDSN.full_joined(module_path, local_path)

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

	def items(self, for_module_path: str | None = None) -> Iterator[tuple[str, IReflection]]:
		"""エントリーのイテレーターを取得

		Args:
			for_module_path (str | None): 取得対象のモジュールパス (default = None)
		Returns:
			Iterator[tuple[str, IReflection]]: イテレーター
		"""
		module_paths = [for_module_path] if for_module_path else self.__items.keys()
		for module_path in module_paths:
			in_module = self.__items[module_path]
			for local_path, value in in_module.items():
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

	def completed(self, module_path: str) -> bool:
		"""モジュールがプリプロセス完了済みか判定

		Args:
			module_path (str): モジュールパス
		Returns:
			bool: True = 完了済み
		"""
		return module_path in self.__completed

	def on_complete(self, module_path: str) -> None:
		"""プリプロセス完了を記録

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

		if module_path in self.__items:
			del self.__items[module_path]

	def to_json(self, serializer: IReflectionSerializer, for_module_path: str | None = None) -> dict[str, DictSerialized]:
		"""JSONデータとして内部データをシリアライズ

		Args:
			serializer (IReflectionSerializer): シンボルシリアライザー
			for_module_path (str | None): 出力モジュールパス (default = None)
		Returns:
			dict[str, DictSerialized]: JSONデータ
		"""
		return {key: serializer.serialize(self[key]) for key in self._order_keys(for_module_path)}

	def load_json(self, serializer: IReflectionSerializer, data: dict[str, DictSerialized]) -> None:
		"""JSONデータを基に内部データをデシリアライズ

		Args:
			serializer (IReflectionSerializer): シンボルシリアライザー
			data (dict[str, DictSerialized]): JSONデータ
		"""
		for key, row in data.items():
			symbol = serializer.deserialize(self, row)
			self[key] = symbol
			if not self.completed(symbol.types.module_path):
				self.on_complete(symbol.types.module_path)

	def _order_keys(self, for_module_path: str | None) -> list[str]:
		"""参照順にキーの一覧を取得

		Args:
			for_module_path (str | None): 出力モジュールパス
		Returns:
			list[str]: キーリスト
		"""
		orders: list[str] = []
		module_paths = [for_module_path] if for_module_path else self.__items.keys()
		for module_path in module_paths:
			in_modules = self.__items[module_path]
			for local_path, symbol in in_modules.items():
				self._order_keys_recursive(for_module_path, symbol, orders)
				key = ModuleDSN.full_joined(module_path, local_path)
				if key not in orders:
					orders.append(key)

		return orders

	def _order_keys_recursive(self, for_module_path: str, symbol: IReflection, orders: list[str]) -> None:
		"""参照順にキーの一覧を更新

		Args:
			for_module_path (str): 出力モジュールパス
			symbol (IReflection): シンボル
			orders (list[str]): キーリスト
		Returns:
			list[str]: キーリスト
		"""
		for attr in symbol.attrs:
			self._order_keys_recursive(for_module_path, attr, orders)

		if not for_module_path or for_module_path == symbol.types.module_path and symbol.types.fullyname not in orders:
			orders.append(symbol.types.fullyname)
