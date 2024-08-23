from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection.base import TraitProvider
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBProvider
from rogw.tranp.semantics.reflection.traits import export_classes


@injectable
def make_db(preprocessors: Preprocessors) -> SymbolDBProvider:
	"""シンボルテーブルプロバイダーを生成

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


@injectable
def trait_provider(invoker: Invoker) -> TraitProvider:
	"""トレイトプロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	"""
	return lambda: [invoker(klass) for klass in export_classes()]

