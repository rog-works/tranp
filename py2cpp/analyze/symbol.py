from enum import Enum
from typing import TypeAlias

from py2cpp.errors import LogicError
from py2cpp.lang.implementation import override
from py2cpp.module.modules import Module
import py2cpp.node.definition as defs

SymbolRaws: TypeAlias = dict[str, 'SymbolRaw']


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。一部属性を保持 (ファンクション)
		Import: Originの複製。属性なし
		Var: Origin/Importを参照。変数として分離し、属性を保持 (変数宣言)
		Reference: Varの参照。属性なし
		Extend: Origin/Importを参照。追加の属性の保持 (タイプ/リテラル)
	Note:
		# 参照関係
		* Origin <- Import
		* Origin <- Var
		* Origin <- Extend
		* Import <- Var
		* Import <- Extend
		* Var <- Reference
	"""
	Origin = 'Origin'
	Import = 'Import'
	Var = 'Var'
	Reference = 'Reference'
	Extend = 'Extend'


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
		return cls(types.fullyname, types, types)

	def __init__(self, ref_path: str, types: defs.ClassDef, decl: defs.Decl, via: 'SymbolRaw | None' = None, role: Roles = Roles.Origin) -> None:
		"""インスタンスを生成

		Args:
			ref_path (str): 参照パス
			types (ClassDef): クラス定義ノード
			decl (Decl): 宣言ノード
			via (SymbolRaw | None): 参照元のシンボル
			role (str): シンボルの役割
		"""
		self._ref_path = ref_path
		self._types = types
		self._decl = decl
		self._attrs: list[SymbolRaw] = []
		self._via = via
		self._role = role

	@property
	def ref_path(self) -> str:
		"""str: 参照パス"""
		return self._ref_path

	@property
	def org_path(self) -> str:
		"""str: 参照パス(オリジナル)"""
		return self.types.fullyname

	@property
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self._types

	@property
	def decl(self) -> defs.Decl:
		"""Decl: 宣言ノード"""
		return self._decl

	@property
	def attrs(self) -> list['SymbolRaw']:
		"""list[SymbolRaw]: 属性シンボルリスト"""
		if self._attrs:
			return self._attrs

		return self._via.attrs if self._via else []

	@property
	def via(self) -> 'SymbolRaw | None':
		"""SymbolRaw | None: 参照元のシンボル"""
		return self._via

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self._role in [Roles.Origin, Roles.Var, Roles.Extend]

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
		return self.ref_path.replace(self.types.module_path, module.path)

	def to(self, module: Module) -> 'SymbolRaw':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), types=self.types, decl=self.decl, via=self, role=Roles.Import)

	def wrap(self, decl: defs.Decl) -> 'SymbolRaw':
		"""シンボルをラップ

		Args:
			decl (Decl): 宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		to_roles = {
			defs.DeclVars: Roles.Var,
			defs.DeclRefs: Roles.Reference,
			defs.DeclWraps: Roles.Extend,
		}
		role = [role for with_types, role in to_roles.items() if isinstance(decl, with_types)].pop()
		return SymbolRaw(self.ref_path, types=self.types, decl=decl, via=self, role=role)

	def extends(self, *attrs: 'SymbolRaw') -> 'SymbolRaw':
		"""シンボルが保持する型を拡張情報として属性に取り込む

		Args:
			*attrs (SymbolRaw): 属性シンボルリスト
		Returns:
			SymbolRaw: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行
			LogicError: 拡張済みのインスタンスに再度実行
		"""
		if not self.has_entity:
			raise LogicError(f'Not allowd operation. symbol: {self.types.fullyname}, role: {self._role}')

		if self._attrs:
			raise LogicError(f'Already set attibutes. symbol: {self.types.fullyname}')

		self._attrs = list(attrs)
		return self


