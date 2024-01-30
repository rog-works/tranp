from py2cpp.analize.db import SymbolDB
from py2cpp.analize.symbol import SymbolRaws
from py2cpp.analize.symbols import Symbols
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs


class ResolveUnknown:
	"""Unknownのシンボルを解決"""

	def __call__(self, module_path: ModulePath, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			module_path (ModulePath): モジュールパス
			db (SymbolDB): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		symbols = Symbols(module_path, SymbolDB(raws))
		update_raws: SymbolRaws = {}
		for key, raw in raws.items():
			if isinstance(raw.decl, defs.MoveAssign):
				update_raws[key] = symbols.type_of(raw.decl.value).raw.varnize(raw.decl)

		return {**raws, **update_raws}
