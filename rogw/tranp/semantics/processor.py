from typing import Protocol

from rogw.tranp.semantics.reflection import SymbolDB


class Preprocessor(Protocol):
	"""プリプロセッサープロトコル"""

	def __call__(self, raws: SymbolDB) -> SymbolDB:
		"""シンボルテーブルを生成

		Args:
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
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
