from py2cpp.analyze.finder import SymbolFinder
from py2cpp.analyze.symbol import SymbolRaws
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class ResolveTypeAlias:
	"""TypeAliasのシンボルを解決"""

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
		update_raws: SymbolRaws = {}
		for key, raw in raws.items():
			if isinstance(raw.decl, defs.AltClass):
				update_raws[key] = raw.to_alias(self.finder.by_symbolic(raws, raw.decl.actual_type).types)

		return {**raws, **update_raws}
