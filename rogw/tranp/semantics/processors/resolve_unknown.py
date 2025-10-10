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
		```
		### Unknownになる条件
		* MoveAssignの代入変数
		* For/CompForの展開変数
		* WithEntryの展開変数
		```
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
			True = 後続処理を実行
		"""
		for _, raw in db.items(module.path):
			if not isinstance(raw.decl, defs.Declable):
				continue

			if isinstance(raw.decl.declare, defs.MoveAssign) and isinstance(raw.decl.declare.var_type, defs.Empty):
				raw.mod_on('origin', self.make_mod_right_to_left(raw, raw.decl.declare.value))
			elif isinstance(raw.decl.declare, (defs.For, defs.CompFor)):
				raw.mod_on('origin', self.make_mod_right_to_left(raw, raw.decl.declare.for_in))
			elif isinstance(raw.decl.declare, defs.WithEntry):
				raw.mod_on('origin', self.make_mod_right_to_left(raw, raw.decl.declare.enter))
			elif isinstance(raw.decl.declare, defs.Lambda):
				raw.mod_on('origin', self.make_mod_lambda_param(raw, raw.decl.declare))

		return True

	def make_mod_right_to_left(self, var_raw: IReflection, value_node: Node) -> Mod:
		"""モッドを生成(右辺値解決用)

		Args:
			var_raw: 変数宣言シンボル
			value_node: 右辺値ノード
		Returns:
			モッド
		"""
		return lambda: [self.invoker(self.resolve_right_to_left, var_raw, value_node)]

	def make_mod_lambda_param(self, var_raw: IReflection, declare: defs.Lambda) -> Mod:
		"""モッドを生成(ラムダ引数用)

		Args:
			var_raw: 変数宣言シンボル
			declare: ラムダ
		Returns:
			モッド
		"""
		return lambda: [self.invoker(self.resolve_lambda_param, var_raw, declare)]

	@injectable
	def resolve_right_to_left(self, reflections: Reflections, var_raw: IReflection, value_node: Node) -> IReflection:
		"""右辺値の型を解決し、変数宣言シンボルを生成

		Args:
			reflections: シンボルリゾルバー @inject
			var_raw: 変数宣言シンボル
			value_node: 右辺値ノード
		Returns:
			シンボル
		"""
		value_raw = reflections.type_of(value_node)
		decl_vars = as_a(IDeclaration, var_raw.decl.declare).symbols
		if len(decl_vars) == 1:
			return var_raw.declare(var_raw.node.as_a(defs.Declable), value_raw)

		index = decl_vars.index(var_raw.decl)
		actual_value_raw = value_raw.attrs[0] if value_raw.types.is_a(defs.AltClass) else value_raw
		return var_raw.declare(var_raw.node.as_a(defs.Declable), actual_value_raw.attrs[index])

	@injectable
	def resolve_lambda_param(self, reflections: Reflections, var_raw: IReflection, declare: defs.Lambda) -> IReflection:
		"""依存する型を解決し、引数宣言シンボルを生成

		Args:
			reflections: シンボルリゾルバー @inject
			var_raw: 変数宣言シンボル
			lambda: ラムダ
		Returns:
			シンボル
		"""
		decl_vars = as_a(IDeclaration, declare).symbols
		index = decl_vars.index(var_raw.decl)
		parent = declare.parent
		if isinstance(parent, defs.AnnoAssign):
			# 期待値: var: Callable[[A, B]: ...] = lambda a, b: ...
			type_raw = reflections.type_of(parent)
			return var_raw.declare(var_raw.node.as_a(defs.Declable), type_raw.attrs[index])
		elif isinstance(parent, defs.Argument):
			# 期待値: func(lambda a, b: ...)
			func_call = parent.parent.as_a(defs.FuncCall)
			func_raw = reflections.type_of(func_call.calls)
			is_method = isinstance(func_raw.types, (defs.Constructor, defs.Method, defs.ClassMethod))
			arg_index = func_call.arguments.index(parent)
			arg_raw = func_raw.attrs[arg_index + (1 if is_method else 0)]
			return var_raw.declare(var_raw.node.as_a(defs.Declable), arg_raw.attrs[index])
		else:
			# 期待値: (lambda a, b: ...)(a_value, b_value)
			arg = as_a(defs.Group, parent).parent.as_a(defs.FuncCall).arguments[index]
			arg_raw = reflections.type_of(arg)
			return var_raw.declare(var_raw.node.as_a(defs.Declable), arg_raw)
