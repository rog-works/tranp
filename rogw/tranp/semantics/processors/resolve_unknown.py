from typing import Callable, cast

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.syntax.node.promise import IDeclaration
from rogw.tranp.semantics.reflection import IReflection, SymbolProxy, SymbolDB
from rogw.tranp.semantics.reflections import Reflections


class ResolveUnknown:
	"""Unknownのシンボルを解決

	Note:
		# Unknownになる条件
		* MoveAssignの代入変数
		* For/CompForの展開変数
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

		for key, raw in db.items():
			if not isinstance(raw.decl, defs.Declable):
				continue

			if isinstance(raw.decl.declare, defs.MoveAssign):
				db[key] = SymbolProxy(raw, self.make_resolver(raw, raw.decl.declare.value))
			elif isinstance(raw.decl.declare, (defs.For, defs.CompFor)):
				db[key] = SymbolProxy(raw, self.make_resolver(raw, raw.decl.declare.for_in))

		return db

	@injectable
	def resolver(self, reflections: Reflections, var_raw: IReflection, value_node: Node) -> IReflection:
		"""シンボルの右辺値を解決したシンボルを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			var_raw (IReflection): 変数宣言シンボル
			value_node (Node): 右辺値ノード
		Returns:
			IReflection: 解決したシンボル
		Note:
			変数宣言のシンボルのため、RolesをVarに変更
		"""
		return self.unpack_value(var_raw, reflections.type_of(value_node)).to.var(var_raw.decl.as_a(defs.DeclVars))

	def make_resolver(self, raw: IReflection, value_node: Node) -> Callable[[], IReflection]:
		"""シンボルリゾルバーを生成

		Args:
			var_raw (IReflection): 変数宣言シンボル
			value_node (Node): 右辺値ノード
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.resolver, raw, value_node)

	def unpack_value(self, var_raw: IReflection, value_raw: IReflection) -> IReflection:
		"""右辺値の型をアンパックして左辺の変数の型を解決

		Args:
			var_raw (IReflection): 変数宣言シンボル
			value_raw (IReflection): 変数宣言時の右辺値シンボル
		Returns:
			IReflection: 変数の型
		"""
		decl_vars = cast(IDeclaration, var_raw.decl.declare).symbols
		if len(decl_vars) == 1:
			return value_raw

		index = decl_vars.index(var_raw.decl)
		return value_raw.attrs[index]
