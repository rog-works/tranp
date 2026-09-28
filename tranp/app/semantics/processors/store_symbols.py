from tranp.app.lang.annotation import duck_typed, injectable
from tranp.app.module.module import Module
from tranp.app.semantics.processor import Preprocessor
from tranp.app.semantics.reflection.db import SymbolDB
from tranp.app.semantics.reflection.persistent import ISymbolDBPersistor


class StoreSymbols:
	"""シンボルテーブルを永続化。プリプロセスの最後の実行"""

	@injectable
	def __init__(self, persistor: ISymbolDBPersistor) -> None:
		"""インスタンスを生成

		Args:
			persistor: シンボルテーブル永続化 @inject
		"""
		self.persistor = persistor

	@duck_typed(Preprocessor)
	def __call__(self, module: Module, db: SymbolDB) -> bool:
		"""シンボルテーブルを編集

		Args:
			module: モジュール
			db: シンボルテーブル
		Returns:
			True = 後続処理を実行
		"""
		db.on_complete(module.path)
		self.persistor.store(module, db)
		return True
