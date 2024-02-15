from typing import cast

from rogw.tranp.analyze.finder import SymbolFinder
from rogw.tranp.analyze.symbol import SymbolRaw, SymbolRaws
from rogw.tranp.lang.implementation import injectable
import rogw.tranp.node.definition as defs


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

			decl_type = self.fetch_decl_type(raw)
			if isinstance(decl_type, defs.GenericType):
				update_raws[key] = self.apply_generic(raws, raw, decl_type)
			elif isinstance(decl_type, defs.Function):
				update_raws[key] = self.apply_function(raws, raw, decl_type)
			elif isinstance(decl_type, defs.AltClass):
				update_raws[key] = self.apply_alt_class(raws, raw, decl_type)
			elif isinstance(decl_type, defs.Class):
				update_raws[key] = self.apply_class(raws, raw, decl_type)

		return {**raws, **update_raws}

	def fetch_decl_type(self, raw: SymbolRaw) -> defs.Type | defs.ClassDef | None:
		"""シンボルの型(タイプ/クラス定義ノード)を取得。型が不明な場合はNoneを返却

		Args:
			raw (SymbolRaw): シンボル
		Returns:
			Type | ClassDef | None: タイプ/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(raw.decl.declare, defs.Parameter):
			# XXX self/cls以外は型指定がある前提
			if raw.decl.declare.var_type.is_a(defs.Type):
				return raw.decl.declare.var_type.as_a(defs.Type)
		elif isinstance(raw.decl.declare, (defs.AnnoAssign, defs.Catch)):
			return raw.decl.declare.var_type
		elif isinstance(raw.decl.declare, defs.ClassDef):
			return raw.decl.declare

		# MoveAssign, For
		# 型指定が無いため全てUnknown
		return None

	def expand_attr(self, raws: SymbolRaws, t_raw: SymbolRaw, t_type: defs.Type) -> SymbolRaw:
		"""タイプノードを属性として展開

		Args:
			raws (SymbolRaws): シンボルテーブル
			t_raw (SymbolRaw): タイプノードのシンボル
			t_type (Type): タイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		if not isinstance(t_type, defs.GenericType):
			return t_raw

		return self.apply_generic(raws, t_raw, t_type)

	def apply_generic(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
		"""ジェネリックタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			generic_type (GenericType): ジェネリックタイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = []
		for t_type in generic_type.template_types:
			t_raw = self.finder.by_symbolic(raws, t_type).to_generic(t_type)
			attrs.append(self.expand_attr(raws, t_raw, t_type))

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
				t_raw = self.finder.by_symbolic(raws, t_type).to_var(parameter)
				attrs.append(self.expand_attr(raws, t_raw, t_type))

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
		attrs = [self.finder.by_symbolic(raws, generic_type) for generic_type in types.generic_types]
		return via.extends(*attrs)
