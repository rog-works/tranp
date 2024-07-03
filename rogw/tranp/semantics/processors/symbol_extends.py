from typing import Callable, cast

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.reflection.proxy import SymbolProxy
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.reflection import IReflection, Roles, SymbolDB


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
		for key, raw in db.items_in_preprocess():
			if raw.origin.role == Roles.Origin:
				if isinstance(raw.types, defs.AltClass):
					db[key] = SymbolProxy(raw, self.make_resolver_for_alt_class(raw))
				elif isinstance(raw.types, defs.Class):
					db[key] = SymbolProxy(raw, self.make_resolver_for_class(raw))
				elif isinstance(raw.types, defs.Function):
					db[key] = SymbolProxy(raw, self.make_resolver_for_function(raw))
			elif raw.role == Roles.Var:
				if isinstance(raw.decl.declare, defs.Parameter) and isinstance(raw.decl.declare.var_type, defs.Type):
					db[key] = SymbolProxy(raw, self.make_resolver_for_var(raw, raw.decl.declare.var_type))
				elif isinstance(raw.decl.declare, (defs.AnnoAssign, defs.Catch)):
					db[key] = SymbolProxy(raw, self.make_resolver_for_var(raw, raw.decl.declare.var_type))

		return db
	
	def make_resolver_for_alt_class(self, raw: IReflection) -> Callable[[], IReflection]:
		"""シンボルリゾルバーを生成(タイプ再定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.extends_for_alt_class, raw, raw.types)

	def make_resolver_for_class(self, raw: IReflection) -> Callable[[], IReflection]:
		"""シンボルリゾルバーを生成(クラス定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.extends_for_class, raw, raw.types)

	def make_resolver_for_function(self, raw: IReflection) -> Callable[[], IReflection]:
		"""シンボルリゾルバーを生成(ファンクション定義用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.extends_for_function, raw, raw.types)

	def make_resolver_for_var(self, raw: IReflection, decl_type: defs.Type) -> Callable[[], IReflection]:
		"""シンボルリゾルバーを生成(変数宣言用)

		Args:
			raw (IReflection): シンボル
		Returns:
			Callable[[], IReflection]: シンボルリゾルバー
		"""
		return lambda: self.invoker(self.extends_for_var, raw, decl_type)

	def extends_for_function(self, reflections: Reflections, via: IReflection, function: defs.Function) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(ファンクション定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
			function (Function): ファンクションノード
		Returns:
			IReflection: シンボル
		"""
		attrs: list[IReflection] = []
		for parameter in function.parameters:
			# XXX cls/selfにタイプヒントが無い場合のみ補完
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)) and parameter.var_type.is_a(defs.Empty):
				attrs.append(reflections.resolve(parameter.symbol))
			else:
				parameter_type = cast(defs.Type, parameter.var_type)
				attrs.append(reflections.type_of(parameter_type))

		attrs.append(reflections.type_of(function.return_type))
		return via.extends(*attrs)

	def extends_for_alt_class(self, reflections: Reflections, via: IReflection, alt_types: defs.AltClass) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(タイプ再定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
			alt_types (AltClass): タイプ再定義ノード
		Returns:
			IReflection: シンボル
		"""
		return via.extends(reflections.type_of(alt_types.actual_type))

	def extends_for_class(self, reflections: Reflections, via: IReflection, types: defs.Class) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(クラス定義用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
			types (Class): クラス定義ノード
		Returns:
			IReflection: シンボル
		"""
		def fetch_template_attrs(for_types: defs.Class) -> list[IReflection]:
			attrs: list[IReflection] = []
			for template_type in for_types.template_types:
				candidate = reflections.type_of(template_type)
				if candidate.decl.is_a(defs.TemplateClass):
					attrs.append(candidate)

			return attrs

		attrs = fetch_template_attrs(types)
		for inherit in types.inherits:
			inherit_attrs = fetch_template_attrs(reflections.type_of(inherit).types.as_a(defs.Class))
			attrs.extend([attr for attr in inherit_attrs if attr not in attrs])

		return via.extends(*attrs)

	def extends_for_var(self, reflections: Reflections, via: IReflection, decl_type: defs.Type) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(変数宣言用)

		Args:
			reflections (Reflections): シンボルリゾルバー
			via (IReflection): シンボル
			decl_type (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		return via.extends(*reflections.type_of(decl_type).attrs)
