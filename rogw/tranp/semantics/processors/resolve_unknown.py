from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.processor import Preprocessor
from rogw.tranp.semantics.reflection.base import Mod, IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB
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
			invoker: ファクトリー関数 @inject
		"""
		self.invoker = invoker

	@duck_typed(Preprocessor)
	def __call__(self, module: Module, db: SymbolDB) -> bool:
		"""シンボルテーブルを編集

		Args:
			module: モジュール
			db: シンボルテーブル
		Returns:
			bool: True = 後続処理を実行
		"""
		for _, raw in db.items(module.path):
			if not isinstance(raw.decl, defs.Declable):
				continue

			if isinstance(raw.decl.declare, defs.MoveAssign) and isinstance(raw.decl.declare.var_type, defs.Empty):
				raw.mod_on('origin', self.make_mod(raw, raw.decl.declare.value))
			elif isinstance(raw.decl.declare, (defs.For, defs.CompFor)):
				raw.mod_on('origin', self.make_mod(raw, raw.decl.declare.for_in))
			elif isinstance(raw.decl.declare, defs.WithEntry):
				raw.mod_on('origin', self.make_mod(raw, raw.decl.declare.enter))

		return True


	def make_mod(self, raw: IReflection, value_node: Node) -> Mod:
		"""モッドを生成

		Args:
			var_raw: 変数宣言シンボル
			value_node: 右辺値ノード
		Returns:
			Mod: モッド
		"""
		return lambda: [self.invoker(self.resolve_right_value, raw, value_node)]

	@injectable
	def resolve_right_value(self, reflections: Reflections, var_raw: IReflection, value_node: Node) -> IReflection:
		"""右辺値の型を解決し、変数宣言シンボルを生成

		Args:
			reflections: シンボルリゾルバー @inject
			var_raw: 変数宣言シンボル
			value_node: 右辺値ノード
		Returns:
			IReflection: シンボル
		"""
		value_raw = reflections.type_of(value_node)
		decl_vars = as_a(IDeclaration, var_raw.decl.declare).symbols
		if len(decl_vars) == 1:
			return var_raw.declare(var_raw.node.as_a(defs.Declable), value_raw)

		index = decl_vars.index(var_raw.decl)
		actual_value_raw = value_raw.attrs[0] if value_raw.types.is_a(defs.AltClass) else value_raw
		return var_raw.declare(var_raw.node.as_a(defs.Declable), actual_value_raw.attrs[index])
