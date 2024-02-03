from typing import cast

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
			elif isinstance(domain_type, defs.Function):
				update_raws[key] = self.__actualize_function(raws, raw, domain_type)

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
			return raw.decl

	def __expand_attr(self, raws: SymbolRaws, t_raw: SymbolRaw, t_type: defs.Type) -> SymbolRaw:
		"""指定のタイプノードを属性として展開

		Args:
			raws (SymbolRaws): シンボルテーブル
			t_raw: (SymbolRaw): タイプノードのシンボル
			t_type (Type): タイプノード
		"""
		return self.__actualize_generic(raws, t_raw, t_type) if isinstance(t_type, defs.GenericType) else t_raw

	def __actualize_generic(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
		"""ジェネリックタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via: (SymbolRaw): シンボル
			generic_type (GenericType): ジェネリックタイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs = [self.__expand_attr(raws, SymbolResolver.by_symbolic(raws, t_type), t_type) for t_type in generic_type.template_types]
		return via.extends(*attrs)

	def __actualize_function(self, raws: SymbolRaws, via: SymbolRaw, function: defs.Function) -> SymbolRaw:
		"""ファンクションノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via: (SymbolRaw): シンボル
			function (Function): ファンクションノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = []
		for parameter in function.parameters:
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)):
				attrs.append(SymbolResolver.by_symbolic(raws, parameter.symbol))
			else:
				t_type = cast(defs.Type, parameter.var_type)
				t_raw = SymbolResolver.by_symbolic(raws, t_type)
				attrs.append(self.__expand_attr(raws, t_raw.varnize(parameter), t_type))

		t_raw = SymbolResolver.by_symbolic(raws, function.return_type).returnize(function.return_type)
		attrs.append(self.__expand_attr(raws, t_raw, function.return_type))
		return via.extends(*attrs)
