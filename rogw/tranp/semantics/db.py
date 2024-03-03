from rogw.tranp.lang.implementation import injectable
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection import SymbolRaws, SymbolDB


@injectable
def make_db(preprocessors: Preprocessors) -> SymbolDB:
	"""シンボルテーブルを生成

	Args:
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		SymbolDB: シンボルテーブル
	"""
	raws = SymbolRaws()
	for proc in preprocessors():
		raws = proc(raws)

	return SymbolDB(raws)
