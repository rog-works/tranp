from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.processors.from_modules import FromModules
from rogw.tranp.semantics.processors.resolve_generic import ResolveGeneric
from rogw.tranp.semantics.processors.resolve_unknown import ResolveUnknown


@injectable
def preprocessors(invoker: Invoker) -> Preprocessors:
	"""プリプロセッサープロバイダーを生成

	Args:
		invoker (Invoker): ファクトリー関数 @inject
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	ctors = [
		FromModules,
		ResolveGeneric,
		ResolveUnknown,
	]
	return lambda: [invoker(proc) for proc in ctors]
