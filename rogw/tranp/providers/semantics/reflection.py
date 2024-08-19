from rogw.tranp.lang.annotation import injectable
from rogw.tranp.semantics.reflection.interface import SymbolDB, SymbolDBProvider
from rogw.tranp.semantics.processor import Preprocessors


@injectable
def make_db(preprocessors: Preprocessors) -> SymbolDBProvider:
	"""シンボルテーブルを生成

	Args:
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		SymbolDBProvider: シンボルテーブルプロバイダー
	"""
	db = SymbolDB()
	for proc in preprocessors():
		db = proc(db)

	return SymbolDBProvider(db)
