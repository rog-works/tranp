from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.processor import Preprocessor
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.persistent import ISymbolDBPersistor


class PersistSymbols:
	"""シンボルテーブルを永続化"""

	@injectable
	def __init__(self, persistor: ISymbolDBPersistor) -> None:
		"""インスタンスを生成

		Args:
			persistor (ISymbolDBPersistor): シンボルテーブル永続化 @inject
		"""
		self.persistor = persistor

	@duck_typed(Preprocessor)
	def __call__(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを編集

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		self.persistor.store(module, db)
