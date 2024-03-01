from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterator, Self, TypeVar

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

T_Raw = TypeVar('T_Raw', bound='IReflection')


class Roles(Enum):
	"""シンボルの役割

	Attributes:
		Origin: 定義元。クラス定義ノードが対象。属性は保有しない
		Import: Originの複製。属性は保有しない
		Class: クラス定義ノードが対象。クラスはGeneric型、ファンクションは関数シグネチャーを属性として保有
		Var: 変数宣言ノードが対象。Generic型の属性を保有
		Generic: タイプノードが対象。Generic型の属性を保有
		Literal: リテラルノードが対象。Generic型の属性を保有
		Reference: 参照系ノードが対象。属性は保有しない
	"""
	Origin = 'Origin'
	Import = 'Import'
	Class = 'Class'
	Var = 'Var'
	Generic = 'Generic'
	Literal = 'Literal'
	Reference = 'Reference'
	Result = 'Result'

	@property
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		return self in [Roles.Origin, Roles.Class, Roles.Var, Roles.Generic, Roles.Literal]


class Container(dict[str, T_Raw]):
	"""シンボルテーブル"""

	@classmethod
	def new(cls, *raws: Self | dict[str, T_Raw]) -> Self:
		"""シンボルテーブルを結合した新たなインスタンスを生成

		Args:
			*raws (Self | dict[str, T_Raw]): シンボルテーブルリスト
		Returns:
			Self: 生成したインスタンス
		"""
		raise NotImplementedError()

	def merge(self, *raws: Self | dict[str, T_Raw]) -> Self:
		"""指定のシンボルテーブルと結合

		Args:
			*raws (Self | dict[str, T_Raw]): シンボルテーブルリスト
		Returns:
			Self: 自己参照
		"""
		raise NotImplementedError()


class IWrapper:
	"""ラッパーファクトリー"""
	...


class IReflection(metaclass=ABCMeta):
	"""シンボル

	Attributes:
		ref_fullyname (str): 完全参照名
		org_fullyname (str): 完全参照名(オリジナル)
		types (ClassDef): クラス定義ノード
		decl (DeclAll): クラス/変数宣言ノード
		role (Roles): シンボルの役割
		attrs (list[IReflection]): 属性シンボルリスト
		origin (IReflection | None): スタックシンボル (default = None)
		via (Node | None): 参照元のノード (default = None)
		context (IReflection| None): コンテキストのシンボル (default = None)
	Note:
		# contextのユースケース
		* Relay/Indexerのreceiverを設定。on_func_call等で実行時型の補完に使用
	"""

	@property
	@abstractmethod
	def _raws(self) -> Container:
		"""Container: 所属するシンボルテーブル"""
		...

	@abstractmethod
	def set_raws(self, raws: Container) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			raws (Container): シンボルテーブル
		"""
		...

	@property
	@abstractmethod
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		...

	@property
	@abstractmethod
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		...

	@property
	@abstractmethod
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		...

	@property
	@abstractmethod
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		...

	@property
	@abstractmethod
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		...

	@property
	@abstractmethod
	def attrs(self) -> list['IReflection']:
		"""list[IReflection]: 属性シンボルリスト"""
		...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection | None':
		"""IReflection | None: スタックシンボル"""
		...

	@property
	@abstractmethod
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		...

	@property
	@abstractmethod
	def context(self) -> 'IReflection':
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無い状態で使用
		"""
		...

	@property	
	@abstractmethod
	def has_entity(self) -> bool:
		"""bool: True = 実体を持つ"""
		...

	@abstractmethod
	def clone(self: Self) -> Self:
		"""インスタンスを複製

		Returns:
			Self: 複製したインスタンス
		"""
		...

	@property
	@abstractmethod
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		...

	@abstractmethod
	def hierarchy(self) -> Iterator['IReflection']:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		...

	@abstractmethod
	def extends(self: T_Raw, *attrs: 'IReflection') -> T_Raw:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			T_Raw: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			LogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		...

	@property
	@abstractmethod
	def to(self) -> 'IWrapper':
		"""ラッパーファクトリーを生成

		Returns:
			SymbolWrapper: ラッパーファクトリー
		"""
		...

	@abstractmethod
	def one_of(self, expects: type[T_Raw]) -> T_Raw:
		"""期待する型と同種ならキャスト

		Args:
			expects (type[T_Raw]): 期待する型
		Returns:
			T_Raw: インスタンス
		Raises:
			LogidError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		...
