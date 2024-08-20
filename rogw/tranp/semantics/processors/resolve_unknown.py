from typing import cast

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.interface import Addon, IReflection
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.interface import IDeclaration
from rogw.tranp.syntax.node.node import Node


class ResolveUnknown:
	"""Unknownのシンボルを解決

	Note:
		### Unknownになる条件
		* MoveAssignの代入変数
		* For/CompForの展開変数
		* WithEntryの展開変数
	"""
	@injectable
	def __init__(self, invoker: Invoker) -> None:
		"""インスタンスを生成

		Args:
			invoker (Invoker): ファクトリー関数 @inject
		"""
		self.invoker = invoker

	def __call__(self, db: SymbolDB) -> SymbolDB:
		"""シンボルテーブルを生成

		Args:
			db (SymbolDB): シンボルテーブル @inject
		Returns:
			SymbolDB: シンボルテーブル
		"""

		for raw in db.values():
			if not isinstance(raw.decl, defs.Declable):
				continue

			if isinstance(raw.decl.declare, defs.MoveAssign):
				raw.add_on('origin', self.make_addon(raw, raw.decl.declare.value))
			elif isinstance(raw.decl.declare, (defs.For, defs.CompFor)):
				raw.add_on('origin', self.make_addon(raw, raw.decl.declare.for_in))
			elif isinstance(raw.decl.declare, defs.WithEntry):
				raw.add_on('origin', self.make_addon(raw, raw.decl.declare.enter))

		return db

	def make_addon(self, raw: IReflection, value_node: Node) -> Addon:
		"""アドオンを生成

		Args:
			var_raw (IReflection): 変数宣言シンボル
			value_node (Node): 右辺値ノード
		Returns:
			Addon: アドオン
		"""
		return lambda: [self.invoker(self.resolver, raw, value_node)]

	@injectable
	def resolver(self, reflections: Reflections, var_raw: IReflection, value_node: Node) -> IReflection:
		"""右辺値の型を解決してシンボルを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			var_raw (IReflection): 変数宣言シンボル
			value_node (Node): 右辺値ノード
		Returns:
			IReflection: 解決したシンボル
		"""
		return self.resolve_right_value(var_raw, reflections.type_of(value_node))

	def resolve_right_value(self, var_raw: IReflection, value_raw: IReflection) -> IReflection:
		"""右辺値の型を解決

		Args:
			var_raw (IReflection): 変数宣言シンボル
			value_raw (IReflection): 変数宣言時の右辺値シンボル
		Returns:
			IReflection: 変数の型
		"""
		decl_vars = cast(IDeclaration, var_raw.decl.declare).symbols
		if len(decl_vars) == 1:
			return var_raw.declare(var_raw.node.as_a(defs.Declable), value_raw)

		index = decl_vars.index(var_raw.decl)
		actual_value_raw = value_raw.attrs[0] if value_raw.types.is_a(defs.AltClass) else value_raw
		return var_raw.declare(var_raw.node.as_a(defs.Declable), actual_value_raw.attrs[index])
