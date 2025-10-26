from collections.abc import Iterator, KeysView, MutableMapping, ValuesView

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.errors import Errors
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
			key: キー
		Returns:
			シンボル
		Raises:
			Errors.SymbolNotDefined: 存在しないキーを指定
		"""
		if key in self.__items:
			return self.__items[key]

		raise Errors.SymbolNotDefined(key)

	def __setitem__(self, key: str, symbol: IReflection) -> None:
		"""指定のキーにシンボルを設定

		Args:
			key: キー
			symbol: シンボル
		"""
		if key not in self.__items:
			self.__paths[key] = ModuleDSN.parsed(key)

		self.__items[key] = symbol

	def __delitem__(self, key: str) -> None:
		"""指定のキーのシンボルを削除

		Args:
			key: キー
		Raises:
			Errors.Never: 非対応
		"""
		raise Errors.Never(key)
	
	def __iter__(self) -> Iterator[str]:
		"""キーのイテレーターを取得

		Returns:
			イテレーター
		"""
		for key in self.keys():
			yield key

	def __contains__(self, key: str) -> bool:
		"""指定のキーが存在するか判定

		Args:
			key: キー
		Returns:
			True = 存在
		"""
		return key in self.__items

	def __len__(self) -> int:
		"""エントリーの総数を取得

		Returns:
			エントリーの総数
		"""
		return len(self.__items)

	def items(self, for_module_path: str | None = None) -> Iterator[tuple[str, IReflection]]:
		"""エントリーのイテレーターを取得

		Args:
			for_module_path: 取得対象のモジュールパス (default = None)
		Returns:
			イテレーター
		"""
		if not for_module_path:
			for key, value in self.__items.items():
				yield key, value
		else:
			for key, paths in self.__paths.items():
				if paths[0] == for_module_path:
					yield key, self.__items[key]

	def keys(self) -> KeysView[str]:
		"""キーのジェネレーターを取得

		Returns:
			ジェネレーター
		"""
		return self.__items.keys()

	def values(self) -> ValuesView[IReflection]:
		"""シンボルのジェネレーターを取得

		Returns:
			ジェネレーター
		"""
		return self.__items.values()

	def has_module(self, module_path: str) -> bool:
		"""モジュールが展開済みか判定

		Args:
			module_path: モジュールパス
		Returns:
			True = 展開済み
		"""
		module_paths = [module_path for module_path, _ in self.__paths.values()]
		return module_path in module_paths

	def completed(self, module_path: str) -> bool:
		"""モジュールがプリプロセス完了済みか判定

		Args:
			module_path: モジュールパス
		Returns:
			True = 完了済み
		"""
		return module_path in self.__completed

	def on_complete(self, module_path: str) -> None:
		"""モジュールのプリプロセス完了を記録

		Args:
			module_path: モジュールパス
		"""
		if module_path not in self.__completed:
			self.__completed.append(module_path)

	def unload(self, module_path: str) -> None:
		"""指定モジュール内のシンボルを削除

		Args:
			module_path: モジュールパス
		"""
		if module_path in self.__completed:
			self.__completed.remove(module_path)

		in_module_keys = [key for key in self.__items.keys() if self.__paths[key][0] == module_path]
		for key in in_module_keys:
			del self.__paths[key]
			del self.__items[key]

	def to_json(self, serializer: IReflectionSerializer, for_module_path: str | None = None) -> dict[str, DictSerialized]:
		"""JSONデータとして内部データをシリアライズ

		Args:
			serializer: シンボルシリアライザー
			for_module_path: 出力モジュールパス (default = None)
		Returns:
			JSONデータ
		"""
		return {key: serializer.serialize(self[key]) for key in self._order_keys(for_module_path)}

	def import_json(self, serializer: IReflectionSerializer, data: dict[str, DictSerialized]) -> None:
		"""JSONデータを基に内部データをデシリアライズ。既存データを残したまま追加

		Args:
			serializer: シンボルシリアライザー
			data: JSONデータ
		"""
		for key, row in data.items():
			self[key] = serializer.deserialize(self, row)
			module_path = ModuleDSN.parsed(key)[0]
			if not self.completed(module_path):
				self.on_complete(module_path)

	def _order_keys(self, for_module_path: str | None) -> list[str]:
		"""参照順にキーの一覧を取得

		Args:
			for_module_path: 出力モジュールパス
		Returns:
			キーリスト
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
			for_module_path: 出力モジュールパス
			symbol: シンボル
			orders: キーリスト
		Returns:
			キーリスト
		"""
		for attr in symbol.attrs:
			self._order_keys_recursive(for_module_path, attr, orders)

		if not for_module_path or for_module_path == symbol.types.module_path and symbol.types.fullyname not in orders:
			orders.append(symbol.types.fullyname)
