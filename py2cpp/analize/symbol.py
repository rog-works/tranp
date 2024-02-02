from dataclasses import dataclass, field

from typing import TypeAlias
from py2cpp.errors import LogicError

from py2cpp.lang.implementation import override
from py2cpp.module.modules import Module
import py2cpp.node.definition as defs

Decl: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign | defs.For | defs.Catch | defs.ClassDef | defs.Reference | defs.Indexer | defs.FuncCall | defs.Literal
DeclRefs: TypeAlias = defs.Reference | defs.Indexer | defs.FuncCall | defs.Literal


class SymbolRaw:
	"""シンボル"""

	@classmethod
	def from_types(cls, types: defs.ClassDef) -> 'SymbolRaw':
		"""クラス定義ノードを元にインスタンスを生成

		Args:
			types (ClassDef): クラス定義ノード
		Returns:
			SymbolRaw: シンボル
		"""
		return cls(types.fullyname, types.fullyname, types.module_path, types, types)

	def __init__(self, ref_path: str, org_path: str, module_path: str, types: defs.ClassDef, decl: Decl, via: 'SymbolRaw | None' = None, behavior: str = 'Origin') -> None:
		"""インスタンスを生成

		Args:
			ref_path (str): 参照パス
			org_path (str): 参照パス(オリジナル)
			module_path (str): 展開先モジュールのパス
			types (ClassDef): クラス定義ノード
			decl (Decl): 宣言ノード
			via (SymbolRaw | None): 参照元のシンボル(Reference -> Var -> Type)
		"""
		self._ref_path = ref_path
		self._org_path = org_path
		self._module_path = module_path
		self._types = types
		self._decl = decl
		self._attrs: list[SymbolRaw] = []
		self._via = via
		self._behavior = behavior

	@property
	def ref_path(self) -> str:
		"""str: 参照パス"""
		return self._ref_path

	@property
	def org_path(self) -> str:
		"""str: 参照パス(オリジナル)"""
		return self._org_path

	@property
	def module_path(self) -> str:
		"""str: 展開先モジュールのパス"""
		return self._module_path

	@property
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self._types

	@property
	def decl(self) -> Decl:
		"""Decl: 宣言ノード"""
		return self._decl

	@property
	def attrs(self) -> list['SymbolRaw']:
		"""list[SymbolRaw]: 属性シンボルリスト"""
		if self._attrs:
			return self._attrs

		return self._via.attrs if self._via else []

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実態を持つ"""
		return self._behavior in ['Origin', 'Var']

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
		if other is None:
			return False

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

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module_path, module.path)

	def to(self, module: Module) -> 'SymbolRaw':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), self.org_path, module.path, self.types, self.decl, self, 'Alias')

	def varnize(self, var: defs.DeclVars) -> 'SymbolRaw':
		"""変数シンボル用のデータに変換

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, var.module_path, self.types, var, self, 'Var')

	def refnize(self, ref: DeclRefs) -> 'SymbolRaw':
		"""参照シンボル用のデータに変換

		Args:
			ref (DeclRefs): 参照ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, ref.module_path, self.types, ref, self, 'Reference')

	def extends(self, *attrs: 'SymbolRaw') -> 'SymbolRaw':
		"""属性の型を取り込み、シンボルデータを拡張

		Args:
			*attrs (SymbolRaw): 属性シンボルリスト
		Returns:
			SymbolRaw: インスタンス
		Raises:
			LogicError: 拡張済みのインスタンスに再度実行
		"""
		if self._attrs:
			raise LogicError('Already set attibutes.')

		self._attrs = list(attrs)
		return self


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
