from typing import Callable, NamedTuple

from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.initializers.expand_modules import ExpandModules
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection import DB, SymbolRaws


@injectable
def make_db_origin(invoker: Invoker) -> SymbolDBOrigin:
	db = invoker(ExpandModules())

	initializers: list[Callable[..., DB[str]]] = []
	for initializer in initializers:
		db = initializer(db)

	return SymbolDBOrigin(db)


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
