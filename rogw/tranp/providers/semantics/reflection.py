from rogw.tranp.lang.implementation import injectable
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection import SymbolDB, SymbolDBProvider


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
