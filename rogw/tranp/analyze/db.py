from typing import NamedTuple

from rogw.tranp.analyze.processor import Preprocessors
from rogw.tranp.analyze.symbol import SymbolRaws
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker


class SymbolDB(NamedTuple):
	"""シンボルテーブルを管理

	Attributes:
		raws: シンボルテーブル
	"""

	raws: SymbolRaws


@injectable
def make_db(invoker: Invoker, preprocessors: Preprocessors) -> SymbolDB:
	"""シンボルテーブルを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		SymbolDB: シンボルテーブル
	"""
	raws = SymbolRaws()
	for proc in preprocessors():
		raws = invoker(proc, raws)

	return SymbolDB(raws)
