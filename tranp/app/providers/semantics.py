from collections.abc import Iterator

from tranp.app.lang.annotation import injectable
from tranp.app.lang.locator import Invoker
from tranp.app.lang.trait import TraitProvider
from tranp.app.semantics.processor import Preprocessor, PreprocessorProvider
from tranp.app.semantics.processors.expand_modules import ExpandModules
from tranp.app.semantics.processors.resolve_unknown import ResolveUnknown
from tranp.app.semantics.processors.restore_symbols import RestoreSymbols
from tranp.app.semantics.processors.store_symbols import StoreSymbols
from tranp.app.semantics.processors.symbol_extends import SymbolExtends
from tranp.app.semantics.reflection.traits import export_classes


@injectable
def trait_provider(invoker: Invoker) -> TraitProvider:
	"""トレイトプロバイダーを生成

	Args:
		invoker: ファクトリー関数 @inject
	Returns:
		トレイトプロバイダープロバイダー
	"""
	return lambda: [invoker(klass) for klass in export_classes()]


@injectable
def preprocessor_provider(invoker: Invoker) -> PreprocessorProvider:
	"""プリプロセッサープロバイダーを生成

	Args:
		invoker: ファクトリー関数 @inject
	Returns:
		プリプロセッサープロバイダー
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
