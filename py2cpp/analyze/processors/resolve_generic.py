from py2cpp.analyze.symbol import SymbolRaw, SymbolRaws, SymbolResolver
from py2cpp.lang.implementation import injectable
import py2cpp.node.definition as defs


class ResolveGeneric:
	"""Genericのシンボルを解決"""

	@injectable
	def __call__(self, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		update_raws: SymbolRaws = {}
		for key, raw in raws.items():
			if not raw.has_entity:
				continue

			domain_type = self.__fetch_domain_type(raw)
			if isinstance(domain_type, defs.GenericType):
				update_raws[key] = self.__actualize_generic(raws, raw, domain_type)

		return {**raws, **update_raws}

	def __fetch_domain_type(self, raw: SymbolRaw) -> defs.Type | defs.Class | defs.Function | None:
		"""シンボルの型(タイプ/クラス定義ノード)を取得。型が不明な場合はNoneを返却

		Args:
			raw (SymbolRaw): シンボル
		Returns:
			Type | Class | Function | None: タイプ/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(raw.decl, (defs.AnnoAssign, defs.Catch)):
			return raw.decl.var_type
		elif isinstance(raw.decl, defs.Parameter):
			if isinstance(raw.decl.symbol, defs.DeclClassParam):
				return raw.decl.symbol.class_types.as_a(defs.Class)
			elif isinstance(raw.decl.symbol, defs.DeclThisParam):
				return raw.decl.symbol.class_types.as_a(defs.Class)
			else:
				return raw.decl.var_type.as_a(defs.Type)
		elif isinstance(raw.decl, (defs.MoveAssign, defs.For)):
			# 型指定が無いため全てUnknown
			return None
		elif isinstance(raw.decl, defs.Function):
			return raw.decl.return_type

	def __actualize_generic(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
		"""ジェネリックタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via: (SymbolRaw): シンボル
			generic_type (GenericType): ジェネリックタイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = []
		for t_type in generic_type.template_types:
			t_raw = SymbolResolver.by_type(raws, t_type)
			if isinstance(t_raw.types, defs.GenericType):
				attrs.append(self.__actualize_generic(raws, t_raw, t_raw.types))
			else:
				attrs.append(t_raw)

		return via.extends(*attrs)
