from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.processor import Preprocessor
from rogw.tranp.semantics.reflection.base import Mod, IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


class SymbolExtends:
	"""シンボルに属性を付与して拡張"""

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
			if raw.node.is_a(defs.ClassDef):
				if isinstance(raw.types, defs.AltClass):
					raw.mod_on('attrs', self.make_mod_for_alt_class(raw))
				elif isinstance(raw.types, defs.Class):
					raw.mod_on('attrs', self.make_mod_for_class(raw))
				elif isinstance(raw.types, defs.Function):
					raw.mod_on('attrs', self.make_mod_for_function(raw))
			elif raw.node.one_of(defs.Parameter, defs.Declable):
				if isinstance(raw.decl.declare, defs.Parameter) and isinstance(raw.decl.declare.var_type, defs.Type):
					raw.mod_on('attrs', self.make_mod_for_var(raw))
				elif isinstance(raw.decl.declare, (defs.AnnoAssign, defs.Catch)):
					raw.mod_on('attrs', self.make_mod_for_var(raw))
				elif isinstance(raw.decl.declare, defs.MoveAssign) and isinstance(raw.decl.declare.var_type, defs.Type):
					raw.mod_on('attrs', self.make_mod_for_var(raw))

		return True
	
	def make_mod_for_alt_class(self, raw: IReflection) -> Mod:
		"""モッドを生成(タイプ再定義用)

		Args:
			raw: シンボル
		Returns:
			モッド
		"""
		return lambda: self.invoker(self.attrs_for_alt_class, raw)

	def make_mod_for_class(self, raw: IReflection) -> Mod:
		"""モッドを生成(クラス定義用)

		Args:
			raw: シンボル
		Returns:
			モッド
		"""
		return lambda: self.invoker(self.attrs_for_class, raw)

	def make_mod_for_function(self, raw: IReflection) -> Mod:
		"""モッドを生成(ファンクション定義用)

		Args:
			raw: シンボル
		Returns:
			モッド
		"""
		return lambda: self.invoker(self.attrs_for_function, raw)

	def make_mod_for_var(self, raw: IReflection) -> Mod:
		"""モッドを生成(変数宣言用)

		Args:
			raw: シンボル
		Returns:
			モッド
		"""
		return lambda: self.invoker(self.attrs_for_var, raw)

	@injectable
	def attrs_for_function(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、シンボル属性を生成(ファンクション定義用)

		Args:
			reflections: シンボルリゾルバー @inject
			via: シンボル
		Returns:
			シンボル属性
		"""
		func = via.types.as_a(defs.Function)
		attrs: list[IReflection] = []
		for parameter in func.parameters:
			# cls/selfにタイプヒントが無い場合のみ補完
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)) and parameter.var_type.is_a(defs.Empty):
				attrs.append(reflections.type_of(parameter.symbol))
			else:
				parameter_type = parameter.var_type.as_a(defs.Type)
				attrs.append(reflections.type_of(parameter_type))

		attrs.append(reflections.type_of(func.return_type))
		return attrs

	@injectable
	def attrs_for_alt_class(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、シンボル属性を生成(タイプ再定義用)

		Args:
			reflections: シンボルリゾルバー @inject
			via: シンボル
		Returns:
			シンボル属性
		"""
		alt_types = via.types.as_a(defs.AltClass)
		return [reflections.type_of(alt_types.actual_type)]

	@injectable
	def attrs_for_class(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、シンボル属性を生成(クラス定義用)

		Args:
			reflections: シンボルリゾルバー @inject
			via: シンボル
		Returns:
			シンボル属性
		"""
		def fetch_template_attrs(for_types: defs.Class) -> dict[defs.TemplateClass, IReflection]:
			attrs: dict[defs.TemplateClass, IReflection] = {}
			for template_type in for_types.template_types:
				candidate = reflections.type_of(template_type)
				if isinstance(candidate.decl, defs.TemplateClass):
					attrs[candidate.decl] = candidate

			return attrs

		types = via.types.as_a(defs.Class)
		attrs = fetch_template_attrs(types)
		return list(attrs.values())

	@injectable
	def attrs_for_var(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、シンボル属性を生成(変数宣言用)

		Args:
			reflections: シンボルリゾルバー @inject
			via: シンボル
		Returns:
			シンボル属性
		"""
		decl_type = via.decl.declare.one_of(defs.Parameter, defs.MoveAssign, defs.AnnoAssign, defs.Catch).var_type.as_a(defs.Type)
		return reflections.type_of(decl_type).attrs
