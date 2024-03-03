from typing import Callable, cast

from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.syntax.node.promise import IDeclaration
from rogw.tranp.semantics.reflection import IReflection, SymbolRaws
from rogw.tranp.semantics.reflection_impl import SymbolProxy
from rogw.tranp.semantics.symbols import Symbols


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

	def __call__(self, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			raws (SymbolRaws): シンボルテーブル @inject
		Returns:
			SymbolRaws: シンボルテーブル
		"""

		for key, raw in raws.items():
			if not isinstance(raw.decl, defs.Declable):
				continue

			if isinstance(raw.decl.declare, defs.MoveAssign):
				raws[key] = SymbolProxy(raw, self.make_resolver(raw, raw.decl.declare.value))
			elif isinstance(raw.decl.declare, (defs.For, defs.CompFor)):
				raws[key] = SymbolProxy(raw, self.make_resolver(raw, raw.decl.declare.for_in))

		return raws

	@injectable
	def resolver(self, symbols: Symbols, var_raw: IReflection, value_node: Node) -> IReflection:
		"""シンボルの右辺値を解決したシンボルを生成

		Args:
			symbols (Symbols): シンボルリゾルバー @inject
			var_raw (IReflection): 変数宣言シンボル
			value_node (Node): 右辺値ノード
		Returns:
			IReflection: 解決したシンボル
		Note:
			XXX 変数宣言のシンボルのため、roleをVarに変更
		"""
		return self.unpack_value(var_raw, symbols.type_of(value_node)).to.var(var_raw.decl)

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
