from typing import cast

from py2cpp.analyze.finder import SymbolFinder
from py2cpp.analyze.symbol import SymbolRaw, SymbolRaws
from py2cpp.lang.implementation import injectable
import py2cpp.node.definition as defs


class ResolveGeneric:
	"""Genericのシンボルを解決"""

	@injectable
	def __init__(self, finder: SymbolFinder) -> None:
		"""インスタンスを生成

		Args:
			finder (SymbolFinder): シンボル検索 @inject
		"""
		self.finder = finder

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

			domain_type = self.fetch_domain_type(raw)
			if isinstance(domain_type, defs.GenericType):
				update_raws[key] = self.apply_generic(raws, raw, domain_type)
			elif isinstance(domain_type, defs.Function):
				update_raws[key] = self.apply_function(raws, raw, domain_type)
			elif isinstance(domain_type, defs.AltClass):
				update_raws[key] = self.apply_alt_class(raws, raw, domain_type)
			# XXX 文字列表現がGeneric形式になってしまうので一旦廃止
			# elif isinstance(domain_type, defs.Class):
			# 	update_raws[key] = self.apply_class(raws, raw, domain_type)

		return {**raws, **update_raws}

	def fetch_domain_type(self, raw: SymbolRaw) -> defs.Type | defs.ClassDef | None:
		"""シンボルの型(タイプ/クラス定義ノード)を取得。型が不明な場合はNoneを返却

		Args:
			raw (SymbolRaw): シンボル
		Returns:
			Type | ClassDef | None: タイプ/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(raw.decl, (defs.AnnoAssign, defs.Catch)):
			return raw.decl.var_type
		elif isinstance(raw.decl, defs.Parameter):
			# XXX self/cls以外は型指定がある前提
			if raw.decl.var_type.is_a(defs.Type):
				return raw.decl.var_type.as_a(defs.Type)
		elif isinstance(raw.decl, defs.ClassDef):
			return raw.decl
		else:
			# MoveAssign, For
			# 型指定が無いため全てUnknown
			return None

	def expand_attr(self, raws: SymbolRaws, t_raw: SymbolRaw, t_type: defs.Type) -> SymbolRaw:
		"""指定のタイプノードを属性として展開

		Args:
			raws (SymbolRaws): シンボルテーブル
			t_raw (SymbolRaw): タイプノードのシンボル
			t_type (Type): タイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		return self.apply_generic(raws, t_raw, t_type) if isinstance(t_type, defs.GenericType) else t_raw

	def apply_generic(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
		"""ジェネリックタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			generic_type (GenericType): ジェネリックタイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs = [self.expand_attr(raws, self.finder.by_symbolic(raws, t_type).to_generic(t_type), t_type) for t_type in generic_type.template_types]
		return via.extends(*attrs)

	def apply_function(self, raws: SymbolRaws, via: SymbolRaw, function: defs.Function) -> SymbolRaw:
		"""ファンクション定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			function (Function): ファンクションノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = []
		for parameter in function.parameters:
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)):
				attrs.append(self.finder.by_symbolic(raws, parameter.symbol))
			else:
				t_type = cast(defs.Type, parameter.var_type)
				t_raw = self.finder.by_symbolic(raws, t_type)
				attrs.append(self.expand_attr(raws, t_raw.to_var(parameter), t_type))

		t_raw = self.finder.by_symbolic(raws, function.return_type).to_generic(function.return_type)
		attrs.append(self.expand_attr(raws, t_raw, function.return_type))
		return via.extends(*attrs)

	def apply_alt_class(self, raws: SymbolRaws, via: SymbolRaw, types: defs.AltClass) -> SymbolRaw:
		"""タイプ再定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			types (AltClass): タイプ再定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		t_raw = self.finder.by_symbolic(raws, types.actual_type).to_generic(types.actual_type)
		return via.extends(self.expand_attr(raws, t_raw, types.actual_type))

	def apply_class(self, raws: SymbolRaws, via: SymbolRaw, types: defs.Class) -> SymbolRaw:
		"""クラス定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			types (Class): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = [self.finder.by_symbolic(raws, generic_type) for generic_type in types.generic_types]
		return via.extends(*attrs)
