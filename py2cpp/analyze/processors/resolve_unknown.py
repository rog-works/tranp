from py2cpp.analyze.db import SymbolDB
from py2cpp.analyze.finder import SymbolFinder
from py2cpp.analyze.symbol import SymbolRaws
from py2cpp.analyze.symbols import Symbols
from py2cpp.lang.implementation import injectable
import py2cpp.node.definition as defs


class ResolveUnknown:
	"""Unknownのシンボルを解決

	Note:
		# Unknownになる条件
		* MoveAssignの代入変数
		* Forの展開変数
	"""
	@injectable
	def __init__(self, finder: SymbolFinder) -> None:
		"""インスタンスを生成

		Args:
			finder (SymbolFinder): シンボル検索 @inject
		"""
		self.finder = finder

	@injectable
	def __call__(self, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		symbols = Symbols(SymbolDB(raws), self.finder)
		update_raws: SymbolRaws = {}
		for key, raw in raws.items():
			# XXX 変数宣言のシンボルのため、roleをVarに変更
			if isinstance(raw.decl, defs.MoveAssign):
				update_raws[key] = symbols.type_of(raw.decl.value).to_var(raw.decl)
			elif isinstance(raw.decl, defs.For):
				update_raws[key] = symbols.type_of(raw.decl.for_in).to_var(raw.decl)

		return {**raws, **update_raws}
