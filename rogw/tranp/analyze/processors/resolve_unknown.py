from typing import cast

from rogw.tranp.analyze.db import SymbolDB
from rogw.tranp.analyze.finder import SymbolFinder
from rogw.tranp.analyze.symbol import SymbolRaw, SymbolRaws
from rogw.tranp.analyze.symbols import Symbols
from rogw.tranp.lang.implementation import injectable
import rogw.tranp.node.definition as defs
from rogw.tranp.node.promise import IDeclaration


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
		for key, raw in raws.items():
			if not isinstance(raw.decl, defs.Declable):
				continue

			# XXX 変数宣言のシンボルのため、roleをVarに変更
			# XXX MoveAssignを参照するMoveAssign/Forが存在するためrawsを直接更新
			if isinstance(raw.decl.declare, defs.MoveAssign):
				raws[key] = self.unpack_value(raw, symbols.type_of(raw.decl.declare.value))
			elif isinstance(raw.decl.declare, defs.For):
				raws[key] = self.unpack_value(raw, symbols.type_of(raw.decl.declare.for_in))

		return raws

	def unpack_value(self, var_raw: SymbolRaw, value_raw: SymbolRaw) -> SymbolRaw:
		"""右辺値の型をアンパックして左辺の変数の型を解決

		Args:
			var_raw (SymbolRaw): 変数宣言ノード
			value_raw (SymbolRaw): 変数宣言の右辺値ノード
		Returns:
			SymbolRaw: 変数の型
		"""
		decl_vars = cast(IDeclaration, var_raw.decl.declare).symbols
		if len(decl_vars) == 1:
			return value_raw

		index = decl_vars.index(var_raw.decl)
		return value_raw.attrs[index]
