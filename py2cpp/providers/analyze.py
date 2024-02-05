from typing import Callable

from py2cpp.analyze.processor import Preprocessor, Preprocessors
import py2cpp.analyze.processors as procs
from py2cpp.lang.implementation import injectable
from py2cpp.lang.locator import Currying


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
		procs.RuntimeRegister,
	]
	return lambda: [currying(proc, Callable[[], Preprocessor])() for proc in ctors]
