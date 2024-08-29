from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.trait import TraitProvider
from rogw.tranp.module.modules import Modules
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import PreprocessorProvider
from rogw.tranp.semantics.processors.expand_modules import ExpandModules
from rogw.tranp.semantics.processors.persist_symbols import PersistSymbols
from rogw.tranp.semantics.processors.resolve_unknown import ResolveUnknown
from rogw.tranp.semantics.processors.symbol_extends import SymbolExtends
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBFinalizer
from rogw.tranp.semantics.reflection.traits import export_classes


@injectable
def trait_provider(invoker: Invoker) -> TraitProvider:
	"""トレイトプロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	"""
	return lambda: [invoker(klass) for klass in export_classes()]


def plugin_provider_empty() -> PluginProvider:
	"""プラグインプロバイダーを生成(空)

	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	return lambda: []


@injectable
def preprocessor_provider(invoker: Invoker) -> PreprocessorProvider:
	"""プリプロセッサープロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	"""
	ctors = [
		ExpandModules,
		SymbolExtends,
		ResolveUnknown,
		PersistSymbols,
	]
	return lambda: [invoker(ctor) for ctor in ctors]


@injectable
def symbol_db_finalizer(modules: Modules, db: SymbolDB) -> SymbolDBFinalizer:
	"""シンボルテーブル完成プロセスを実行

	Args:
		modules (Modules): モジュールマネジャー @inject
		db (SymbolDB): シンボルテーブル @inject
	Returns:
		SymbolDBFinalizer: シンボルテーブル完成プロセス
	"""
	modules.dependencies()
	return lambda: db
