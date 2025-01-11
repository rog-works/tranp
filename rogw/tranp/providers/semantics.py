from collections.abc import Iterator

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.lang.trait import TraitProvider
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.processor import Preprocessor, PreprocessorProvider
from rogw.tranp.semantics.processors.expand_modules import ExpandModules
from rogw.tranp.semantics.processors.restore_symbols import RestoreSymbols
from rogw.tranp.semantics.processors.store_symbols import StoreSymbols
from rogw.tranp.semantics.processors.resolve_unknown import ResolveUnknown
from rogw.tranp.semantics.processors.symbol_extends import SymbolExtends
from rogw.tranp.semantics.reflection.traits import export_classes


@injectable
def trait_provider(invoker: Invoker) -> TraitProvider:
	"""トレイトプロバイダーを生成

	Args:
		invoker: ファクトリー関数 @inject
	Returns:
		TraitProvider: トレイトプロバイダープロバイダー
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
		invoker: ファクトリー関数 @inject
	Returns:
		PreprocessorProvider: プリプロセッサープロバイダー
	"""
	ctors = [
		RestoreSymbols,
		ExpandModules,
		SymbolExtends,
		ResolveUnknown,
		StoreSymbols,
	]
	def handler() -> Iterator[Preprocessor]:
		for ctor in ctors:
			yield invoker(ctor)

	return handler
