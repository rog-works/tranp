from collections.abc import Iterator
from typing import Protocol

from rogw.tranp.module.module import Module
from rogw.tranp.semantics.reflection.db import SymbolDB


class Preprocessor(Protocol):
	"""プリプロセッサープロトコル"""

	def __call__(self, module: Module, db: SymbolDB) -> bool:
		"""シンボルテーブルを編集

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		Returns:
			bool: True = 後続処理を実行
		"""
		...


class PreprocessorProvider(Protocol):
	"""プリプロセッサープロバイダープロトコル"""

	def __call__(self) -> Iterator[Preprocessor]:
		"""プリプロセッサーのイテレーターを返却

		Returns:
			Iterator[Preprocessor]: イテレーター
		"""
		...
