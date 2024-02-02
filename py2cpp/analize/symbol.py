from dataclasses import dataclass, field

from typing import TypeAlias

from py2cpp.lang.implementation import override
from py2cpp.module.modules import Module
import py2cpp.node.definition as defs

Decl: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign | defs.For | defs.Catch | defs.ClassDef | defs.Reference | defs.Indexer | defs.FuncCall | defs.Literal
DeclRefs: TypeAlias = defs.Reference | defs.Indexer | defs.FuncCall | defs.Literal


class SymbolRaw:
	"""シンボルデータ"""

	def __init__(self, ref_path: str, org_path: str, module_path: str, types: defs.ClassDef, decl: Decl, via: 'SymbolRaw | None' = None, attrs: list['SymbolRaw'] = []) -> None:
		"""インスタンスを生成

		Args:
			ref_path (str): 参照パス
			org_path (str): 参照パス(オリジナル)
			module_path (str): 展開先モジュールのパス
			types (ClassDef): クラス定義ノード
			decl (Decl): 宣言ノード XXX 名称を再検討
			via (SymbolRaw): ラップ対象のシンボル(Reference -> Var -> Type)
			attrs (list[SymbolRaw]): ジェネリック型に対応する属性シンボルリスト
		"""
		self.ref_path = ref_path
		self.org_path = org_path
		self.module_path = module_path
		self.types = types
		self.decl = decl
		self.via = via
		self.attrs = attrs

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		Raises:
			ValueError: Node以外のオブジェクトを指定
		"""
		if type(other) is not SymbolRaw:
			raise ValueError(f'Not allowed comparison. other: {type(other)}')

		return other.__repr__() == self.__repr__()

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		data = {
			'types': self.types.fullyname,
			'attrs': [attr.__repr__() for attr in self.attrs],
		}
		return str(data)

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		if len(self.attrs) > 0:
			attrs = [str(attr) for attr in self.attrs]
			return f'{self.types.domain_name}<{', '.join(attrs)}>'
		else:
			return f'{self.types.domain_name}'

	def to(self, module: Module) -> 'SymbolRaw':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), self.org_path, module.path, self.types, self.decl)

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module_path, module.path)

	def varnize(self, var: defs.DeclVars) -> 'SymbolRaw':
		"""変数シンボル用のデータに変換

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, var.module_path, self.types, var, self)

	def refnize(self, ref: DeclRefs) -> 'SymbolRaw':
		"""参照シンボル用のデータに変換

		Args:
			ref (DeclRefs): 参照ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, ref.module_path, self.types, ref, self)

	def extends(self, *attrs: 'SymbolRaw') -> 'SymbolRaw':
		"""属性を取り込んだ拡張データに変換

		Args:
			*attrs (SymbolRaw): 属性シンボルリスト
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, self.module_path, self.types, self.decl, self.via, list(attrs))


SymbolRaws: TypeAlias = dict[str, SymbolRaw]


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		raws (SymbolRaws): シンボルテーブル
		decl_vars (list[DeclVars]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	raws: SymbolRaws = field(default_factory=dict)
	decl_vars: list[defs.DeclVars] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)
