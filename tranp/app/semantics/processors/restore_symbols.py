from tranp.app.errors import Errors
from tranp.app.lang.annotation import duck_typed, injectable
from tranp.app.module.module import Module
from tranp.app.semantics.processor import Preprocessor
from tranp.app.semantics.reflection.db import SymbolDB
from tranp.app.semantics.reflection.persistent import ISymbolDBPersistor


class RestoreSymbols:
	"""シンボルテーブルを復元。プリプロセスの初めに実行"""

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
		Raises:
			Errors.Never: 実施済みのモジュールに対して再度実行
		"""
		if db.has_module(module.path):
			raise Errors.Never(module, 'Already processing')

		if self.persistor.stored(module):
			self.persistor.restore(module, db)
			return False

		return True
