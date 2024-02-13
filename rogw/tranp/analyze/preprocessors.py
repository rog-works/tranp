from typing import Callable

from rogw.tranp.analyze.processor import Preprocessor, Preprocessors
import rogw.tranp.analyze.processors as procs
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Currying


@injectable
def preprocessors(currying: Currying) -> Preprocessors:
	"""プリプロセッサープロバイダーを生成

	Args:
		currying (Currying): カリー化関数 @inject
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	ctors = [
		procs.FromModules,
		procs.ResolveGeneric,
		procs.ResolveUnknown,
	]
	return lambda: [currying(proc, Callable[[], Preprocessor])() for proc in ctors]
