from typing import cast

from rogw.tranp.lang.annotation import injectable
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.reflection import IReflection, Roles, SymbolDB


class SymbolExtends:
	"""シンボルに属性を付与して拡張"""

	@injectable
	def __init__(self, finder: SymbolFinder) -> None:
		"""インスタンスを生成

		Args:
			finder (SymbolFinder): シンボル検索 @inject
		"""
		self.finder = finder

	def __call__(self, db: SymbolDB) -> SymbolDB:
		"""シンボルテーブルを生成

		Args:
			db (SymbolDB): シンボルテーブル
		Returns:
			SymbolDB: シンボルテーブル
		"""
		for key, raw in db.items():
			if raw.role == Roles.Class:
				if isinstance(raw.types, defs.AltClass):
					db[key] = self.extends_for_alt_class(db, raw, raw.types)
				elif isinstance(raw.types, defs.Class):
					db[key] = self.extends_for_class(db, raw, raw.types)
				elif isinstance(raw.types, defs.Function):
					db[key] = self.extends_for_function(db, raw, raw.types)
			elif raw.role == Roles.Var:
				if isinstance(raw.decl.declare, defs.Parameter) and isinstance(raw.decl.declare.var_type, defs.Type):
					db[key] = self.extends_for_var(db, raw, raw.decl.declare.var_type)
				elif isinstance(raw.decl.declare, (defs.AnnoAssign, defs.Catch)):
					db[key] = self.extends_for_var(db, raw, raw.decl.declare.var_type)

		return db

	def extends_for_function(self, db: SymbolDB, via: IReflection, function: defs.Function) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(ファンクション定義用)

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			function (Function): ファンクションノード
		Returns:
			IReflection: シンボル
		"""
		attrs: list[IReflection] = []
		for parameter in function.parameters:
			# XXX cls/selfにタイプヒントが無い場合のみ補完
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)) and parameter.var_type.is_a(defs.Empty):
				attrs.append(self.finder.by_symbolic(db, parameter.symbol))
			else:
				parameter_type = cast(defs.Type, parameter.var_type)
				parameter_type_raw = self.finder.by_symbolic(db, parameter_type)
				attrs.append(self.extends_for_type(db, parameter_type_raw, parameter_type))

		return_type_raw = self.finder.by_symbolic(db, function.return_type)
		attrs.append(self.extends_for_type(db, return_type_raw, function.return_type))
		return via.extends(*attrs)

	def extends_for_alt_class(self, db: SymbolDB, via: IReflection, alt_types: defs.AltClass) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(タイプ再定義用)

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			alt_types (AltClass): タイプ再定義ノード
		Returns:
			IReflection: シンボル
		"""
		actual_type_raw = self.finder.by_symbolic(db, alt_types.actual_type)
		return via.extends(self.extends_for_type(db, actual_type_raw, alt_types.actual_type))

	def extends_for_class(self, db: SymbolDB, via: IReflection, types: defs.Class) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(クラス定義用)

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			types (Class): クラス定義ノード
		Returns:
			IReflection: シンボル
		"""
		attrs = [self.finder.by_symbolic(db, generic_type) for generic_type in types.generic_types]
		return via.extends(*attrs)

	def extends_for_var(self, db: SymbolDB, via: IReflection, decl_type: defs.Type) -> IReflection:
		"""宣言ノードを解析し、属性の型を取り込みシンボルを拡張(変数宣言用)

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			decl_type (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		return via.extends(*self.extends_for_type(db, via, decl_type).attrs)

	def extends_for_type(self, db: SymbolDB, via: IReflection, decl_type: defs.Type) -> IReflection:
		"""タイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			decl_type (Type): タイプノード
		Returns:
			IReflection: シンボル
		"""
		if isinstance(decl_type, defs.UnionType):
			return self.extends_for_type_by_secondaries(db, via, decl_type, decl_type.or_types)
		elif isinstance(decl_type, defs.GenericType):
			return self.extends_for_type_by_secondaries(db, via, decl_type, decl_type.template_types)
		else:
			return via

	def extends_for_type_by_secondaries(self, db: SymbolDB, via: IReflection, primary_type: defs.GenericType | defs.UnionType, secondary_types: list[defs.Type]) -> IReflection:
		"""ジェネリックタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			db (SymbolDB): シンボルテーブル
			via (IReflection): シンボル
			primary_type (GenericType | UnionType): メインの多様性タイプノード
			secondary_types (list[Type]): サブのタイプノード
		Returns:
			IReflection: シンボル
		"""
		attrs: list[IReflection] = []
		for secondary_type in secondary_types:
			secondary_raw = self.finder.by_symbolic(db, secondary_type)
			attrs.append(self.extends_for_type(db, secondary_raw, secondary_type))

		return via.to.generic(primary_type).extends(*attrs)
