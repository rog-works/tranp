from typing import Callable, NamedTuple

from py2cpp.analyze.processor import Preprocessors
from py2cpp.analyze.symbol import SymbolRaws
from py2cpp.lang.implementation import injectable
from py2cpp.lang.locator import Currying


class SymbolDB(NamedTuple):
	"""シンボルテーブルを管理

	Attributes:
		raws: シンボルテーブル
	"""

	raws: SymbolRaws


@injectable
def make_db(currying: Currying, preprocessors: Preprocessors) -> SymbolDB:
	"""シンボルテーブルを生成

	Args:
		currying (Currying): カリー化関数 @inject
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		SymbolDB: シンボルテーブル
	"""
	raws: SymbolRaws = {}
	for proc in preprocessors():
		invoker = currying(proc, Callable[[SymbolRaws], SymbolRaws])
		raws = invoker(raws)

	return SymbolDB(raws)
