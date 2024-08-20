from typing import cast

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.interface import Addon, IReflection
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


class SymbolExtends:
	"""シンボルに属性を付与して拡張"""

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
			db (SymbolDB): シンボルテーブル
		Returns:
			SymbolDB: シンボルテーブル
		"""
		for _, raw in db.items():
			if raw.node.is_a(defs.ClassDef):
				if isinstance(raw.types, defs.AltClass):
					raw.add_on('attrs', self.make_resolver_for_alt_class(raw))
				elif isinstance(raw.types, defs.Class):
					raw.add_on('attrs', self.make_resolver_for_class(raw))
				elif isinstance(raw.types, defs.Function):
					raw.add_on('attrs', self.make_resolver_for_function(raw))
			elif raw.node.one_of(defs.Parameter, defs.Declable):
				if isinstance(raw.decl.declare, defs.Parameter) and isinstance(raw.decl.declare.var_type, defs.Type):
					raw.add_on('attrs', self.make_resolver_for_var(raw))
				elif isinstance(raw.decl.declare, (defs.AnnoAssign, defs.Catch)):
					raw.add_on('attrs', self.make_resolver_for_var(raw))

		return db
	
	def make_resolver_for_alt_class(self, raw: IReflection) -> Addon:
		"""シンボルリゾルバーを生成(タイプ再定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.attrs_for_alt_class, raw)

	def make_resolver_for_class(self, raw: IReflection) -> Addon:
		"""シンボルリゾルバーを生成(クラス定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.attrs_for_class, raw)

	def make_resolver_for_function(self, raw: IReflection) -> Addon:
		"""シンボルリゾルバーを生成(ファンクション定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.attrs_for_function, raw)

	def make_resolver_for_var(self, raw: IReflection) -> Addon:
		"""シンボルリゾルバーを生成(変数宣言用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.attrs_for_var, raw)

	@injectable
	def attrs_for_function(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(ファンクション定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
		Returns:
			IReflection: シンボル
		"""
		func = via.types.as_a(defs.Function)
		attrs: list[IReflection] = []
		for parameter in func.parameters:
			# XXX cls/selfにタイプヒントが無い場合のみ補完
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)) and parameter.var_type.is_a(defs.Empty):
				attrs.append(reflections.resolve(parameter.symbol))
			else:
				parameter_type = cast(defs.Type, parameter.var_type)
				attrs.append(reflections.type_of(parameter_type))

		attrs.append(reflections.type_of(func.return_type))
		return attrs

	@injectable
	def attrs_for_alt_class(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(タイプ再定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
		Returns:
			IReflection: シンボル
		"""
		alt_types = via.types.as_a(defs.AltClass)
		return [reflections.type_of(alt_types.actual_type)]

	@injectable
	def attrs_for_class(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(クラス定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
		Returns:
			IReflection: シンボル
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
		for inherit in types.inherits:
			inherit_attrs = fetch_template_attrs(reflections.type_of(inherit).types.as_a(defs.Class))
			attrs = {**attrs, **{decl: attr for decl, attr in inherit_attrs.items() if decl not in attrs}}

		return list(attrs.values())

	@injectable
	def attrs_for_var(self, reflections: Reflections, via: IReflection) -> list[IReflection]:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(変数宣言用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
		Returns:
			IReflection: シンボル
		"""
		decl_type = via.decl.declare.one_of(defs.Parameter, defs.AnnoAssign, defs.Catch).var_type
		return reflections.type_of(decl_type).attrs
