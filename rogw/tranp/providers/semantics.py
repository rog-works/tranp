from rogw.tranp.lang.annotation import injectable
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBProvider


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


def plugin_provider_empty() -> PluginProvider:
	"""プラグインプロバイダーを生成(空)

	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	return lambda: []
