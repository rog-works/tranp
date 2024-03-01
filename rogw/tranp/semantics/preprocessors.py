from rogw.tranp.semantics.processor import Preprocessors
import rogw.tranp.semantics.processors as procs
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker


@injectable
def preprocessors(invoker: Invoker) -> Preprocessors:
	"""プリプロセッサープロバイダーを生成

	Args:
		invoker (Inboker): ファクトリー関数 @inject
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	ctors = [
		procs.FromModules,
		procs.ResolveGeneric,
		procs.ResolveUnknown,
	]
	return lambda: [invoker(proc) for proc in ctors]
