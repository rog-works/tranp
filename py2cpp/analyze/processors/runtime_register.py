from py2cpp.analyze.db import SymbolDB
from py2cpp.analyze.symbol import SymbolRaws
from py2cpp.analyze.symbols import Symbols
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class RuntimeRegister:
	"""インライン要素をシンボルに解決

	Note:
		# 登録するインライン要素 # FIXME 暫定
		* FuncCall
		* Literal
	"""

	@injectable
	def __call__(self, modules: Modules, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		# symbols = Symbols(SymbolDB(raws))
		new_raws: SymbolRaws = {}
		# for node in modules.main.entrypoint.calculated():
		# 	if isinstance(node, (defs.Reference, defs.Indexer, defs.FuncCall)):
		# 		new_raws[node.fullyname] = symbols.type_of(node).raw.runtimes(node)
		# 	elif isinstance(node, defs.Literal):
		# 		new_raws[node.fullyname] = symbols.type_of(node).raw.runtimes(node)

		return {**raws, **new_raws}