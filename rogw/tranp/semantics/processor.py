from typing import Protocol

from rogw.tranp.module.module import Module
from rogw.tranp.semantics.reflection.db import SymbolDB


class Preprocessor(Protocol):
	"""プリプロセッサープロトコル"""

	def __call__(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを編集

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		...


class Preprocessors(Protocol):
	"""プリプロセッサープロバイダープロトコル"""

	def __call__(self) -> list[Preprocessor]:
		"""プリプロセッサーリストを返却

		Returns:
			list[Preprocessor]: プリプロセッサーリスト
		"""
		...
