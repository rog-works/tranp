from typing import NamedTuple, Self

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.semantics.reflection.interface import IReflection


class SymbolDB(dict[str, IReflection]):
	"""シンボルテーブル"""

	@classmethod
	def new(cls, *dbs: Self | dict[str, IReflection]) -> Self:
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*dbs (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 生成したインスタンス
		"""
		return cls().merge(*dbs)

	def merge(self, *dbs: Self | dict[str, IReflection]) -> Self:
		"""指定のシンボルテーブルと結合

		Args:
			*dbs (Self | dict[str, IReflection]): シンボルテーブルリスト
		Returns:
			Self: 自己参照
		"""
		for in_db in dbs:
			self.update(**in_db)

		return self

	def sorted(self, module_orders: list[str]) -> Self:
		"""モジュールのロード順に並び替えた新しいインスタンスを生成

		Args:
			module_orders (list[str]): ロード順のモジュール名リスト
		Returns:
			Self: 生成したインスタンス
		"""
		orders = {key: index for index, key in enumerate(module_orders)}
		def order(entry: tuple[str, IReflection]) -> int:
			in_module_path, _ = ModuleDSN.parsed(entry[0])
			return orders.get(in_module_path, -1)

		return self.__class__(dict(sorted(self.items(), key=order)))


class SymbolDBProvider(NamedTuple):
	"""シンボルテーブルプロバイダー"""

	db: SymbolDB
