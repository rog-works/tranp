from typing import Callable

from py2cpp.analize.processor import Preprocessors
from py2cpp.analize.symbol import SymbolRaws
from py2cpp.lang.implementation import injectable
from py2cpp.lang.locator import Currying


class SymbolDB:
	"""シンボルテーブル"""

	@injectable
	def __init__(self, currying: Currying, preprocessors: Preprocessors) -> None:
		"""インスタンスを生成

		Args:
			currying (Currying): カリー化関数 @inject
			preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
		"""
		raws: SymbolRaws = {}
		for proc in preprocessors():
			invoker = currying(proc, Callable[[SymbolRaws], SymbolRaws])
			raws = invoker(raws)

		self.raws = raws
