from typing import TypeAlias, cast

from rogw.tranp.lang.implementation import injectable
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.symbol import SymbolRaw, SymbolRaws

TargetDeclTypes: TypeAlias = defs.GenericType | defs.Function | defs.AltClass | defs.Class


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
		for key, raw in raws.items():
			if not raw.has_entity:
				continue

			decl_type = self.fetch_decl_type(raw)
			if isinstance(decl_type, defs.UnionType):
				raws[key] = self.extends_for_union(raws, raw, decl_type)
			elif isinstance(decl_type, TargetDeclTypes):
				raws[key] = self.extends_generic(raws, raw, decl_type)

		return raws

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

	def extends_generic(self, raws: SymbolRaws, via: SymbolRaw, decl_type: TargetDeclTypes) -> SymbolRaw:
		"""ジェネリックタイプ/クラス定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			decl_type (TargetDeclTypes): ジェネリックタイプ/クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		if isinstance(decl_type, defs.GenericType):
			return self.extends_for_type(raws, via, decl_type)
		elif isinstance(decl_type, defs.Function):
			return self.extends_for_function(raws, via, decl_type)
		elif isinstance(decl_type, defs.AltClass):
			return self.extends_for_alt_class(raws, via, decl_type)
		else:
			return self.extends_for_class(raws, via, decl_type)

	def extends_for_union(self, raws: SymbolRaws, via: SymbolRaw, union_type: defs.UnionType) -> SymbolRaw:
		"""ユニオンタイプノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			union_type (UnionType): ユニオンタイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs: list[SymbolRaw] = []
		for or_type in union_type.or_types:
			t_raw = self.finder.by_symbolic(raws, or_type)
			if isinstance(or_type, defs.UnionType):
				attrs.append(self.extends_for_union(raws, t_raw, or_type))
			elif isinstance(or_type, TargetDeclTypes):
				attrs.append(self.extends_generic(raws, t_raw, or_type))
			else:
				attrs.append(t_raw)

		return via.to.generic(union_type).extends(*attrs)

	def extends_for_type(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
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
			t_raw = self.finder.by_symbolic(raws, t_type)
			attrs.append(self.expand_attr(raws, t_raw, t_type))

		return via.to.generic(generic_type).extends(*attrs)

	def expand_attr(self, raws: SymbolRaws, t_raw: SymbolRaw, t_type: defs.Type) -> SymbolRaw:
		"""タイプノードを属性として展開

		Args:
			raws (SymbolRaws): シンボルテーブル
			t_raw (SymbolRaw): タイプノードのシンボル
			t_type (Type): タイプノード
		Returns:
			SymbolRaw: シンボル
		"""
		if isinstance(t_type, defs.UnionType):
			return self.extends_for_union(raws, t_raw, t_type)
		elif isinstance(t_type, defs.GenericType):
			return self.extends_for_type(raws, t_raw, t_type)
		else:
			return t_raw

	def extends_for_function(self, raws: SymbolRaws, via: SymbolRaw, function: defs.Function) -> SymbolRaw:
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
			# cls/selfにタイプヒントが無い場合のみ補完
			if isinstance(parameter.symbol, (defs.DeclClassParam, defs.DeclThisParam)) and parameter.var_type.is_a(defs.Empty):
				attrs.append(self.finder.by_symbolic(raws, parameter.symbol))
			else:
				t_type = cast(defs.Type, parameter.var_type)
				t_raw = self.finder.by_symbolic(raws, t_type).to.var(parameter)
				attrs.append(self.expand_attr(raws, t_raw, t_type))

		t_raw = self.finder.by_symbolic(raws, function.return_type).to.generic(function.return_type)
		attrs.append(self.expand_attr(raws, t_raw, function.return_type))
		return via.to.types(function).extends(*attrs)

	def extends_for_alt_class(self, raws: SymbolRaws, via: SymbolRaw, types: defs.AltClass) -> SymbolRaw:
		"""タイプ再定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			types (AltClass): タイプ再定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		t_raw = self.finder.by_symbolic(raws, types.actual_type).to.generic(types.actual_type)
		return via.to.types(types).extends(self.expand_attr(raws, t_raw, types.actual_type))

	def extends_for_class(self, raws: SymbolRaws, via: SymbolRaw, types: defs.Class) -> SymbolRaw:
		"""クラス定義ノードを解析し、属性の型を取り込みシンボルを拡張

		Args:
			raws (SymbolRaws): シンボルテーブル
			via (SymbolRaw): シンボル
			types (Class): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		attrs = [self.finder.by_symbolic(raws, generic_type) for generic_type in types.generic_types]
		return via.to.types(types).extends(*attrs)
