from typing import Callable, Iterator

from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.interface import ISymbolProxy, SymbolDB, IReflection, IWrapper, Roles, T_Ref
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class SymbolProxy(IReflection, ISymbolProxy):
	"""シンボルプロクシー
	* 拡張設定を遅延処理
	* 参照順序の自動的な解決
	* 不必要な拡張設定を省略

	Note:
		シンボルの登録順序と参照順序が重要なインスタンスに関して使用 ※現状はResolveUnknownでのみ使用
	"""

	def __init__(self, org_raw: IReflection, extender: Callable[[], IReflection]) -> None:
		"""インスタンスを生成

		Args:
			org_raw (IReflection): オリジナル
			extender (Callable[[], IReflection]): シンボル拡張設定ファクトリー
		"""
		self.__org_raw = org_raw
		self.__extender = extender
		self.__new_raw: IReflection | None = None

	@property
	def __new_raw_proxy(self) -> IReflection:
		"""IReflection: 拡張後のシンボル"""
		if self.__new_raw is None:
			self.__new_raw = self.__extender()

		return self.__new_raw

	@property
	@implements
	def org_raw(self) -> IReflection:
		"""オリジナルのシンボルを取得

		Returns:
			IReflection: オリジナルのシンボル
		Note:
			XXX * プリプロセッサー内で無限ループを防ぐ目的で実装
			XXX * それ以外の目的で使用するのはNG
			@see semantics.reflection.interface.SymbolDB.items_in_preprocess
		"""
		return self.__org_raw

	@property
	@implements
	def _db(self) -> SymbolDB:
		"""SymbolDB: 所属するシンボルテーブル"""
		return self.__org_raw._db

	@implements
	def set_db(self, db: SymbolDB) -> None:
		"""所属するシンボルテーブルを設定

		Args:
			db (SymbolDB): シンボルテーブル
		"""
		self.__org_raw.set_db(db)

	@property
	@implements
	def _actual_addr(self) -> int:
		"""実体のアドレス(ID)を取得

		Returns:
			int: アドレス(ID)
		Note:
			* XXX このメソッドはSymbolProxyによる無限ループを防ぐ目的で実装 @seeを参照
			* XXX 上記以外の目的で使用することは無い
			@see semantics.reflection.implements.Reflection._shared_origin
		"""
		return id(self.__new_raw_proxy)

	@property
	@implements
	def ref_fullyname(self) -> str:
		"""str: 完全参照名"""
		return self.__new_raw_proxy.ref_fullyname

	@property
	@implements
	def org_fullyname(self) -> str:
		"""str: 完全参照名(オリジナル)"""
		return self.__new_raw_proxy.org_fullyname

	@property
	@implements
	def types(self) -> defs.ClassDef:
		"""ClassDef: クラス定義ノード"""
		return self.__new_raw_proxy.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: クラス/変数宣言ノード"""
		return self.__new_raw_proxy.decl

	@property
	@implements
	def role(self) -> Roles:
		"""Roles: シンボルの役割"""
		return self.__new_raw_proxy.role

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return self.__new_raw_proxy.attrs

	@property
	@implements
	def origin(self) -> IReflection | None:
		"""IReflection | None: スタックシンボル"""
		return self.__new_raw_proxy.origin

	@property
	@implements
	def via(self) -> Node | None:
		"""Node | None: 参照元のノード"""
		return self.__new_raw_proxy.via

	@property
	@implements
	def context(self) -> IReflection:
		"""コンテキストを取得

		Returns:
			IReflection: コンテキストのシンボル
		Raises:
			LogicError: コンテキストが無い状態で使用
		"""
		return self.__new_raw_proxy.context

	@implements
	def clone(self) -> IReflection:
		"""インスタンスを複製

		Returns:
			IReflection: 複製したインスタンス
		"""
		return self.__new_raw_proxy.clone()

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return self.__new_raw_proxy.shorthand

	@implements
	def hierarchy(self) -> Iterator[IReflection]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		return self.__new_raw_proxy.hierarchy()

	@implements
	def extends(self, *attrs: IReflection) -> IReflection:
		"""シンボルが保有する型を拡張情報として属性に取り込む

		Args:
			*attrs (IReflection): 属性シンボルリスト
		Returns:
			T_Ref: インスタンス
		Raises:
			LogicError: 実体の無いインスタンスに実行 XXX 出力する例外は要件等
			LogicError: 拡張済みのインスタンスに再度実行 XXX 出力する例外は要件等
		"""
		return self.__new_raw_proxy.extends(*attrs)

	@property
	@implements
	def to(self) -> 'IWrapper':
		"""ラッパーファクトリーを生成

		Returns:
			SymbolWrapper: ラッパーファクトリー
		"""
		return self.__new_raw_proxy.to

	@implements
	def one_of(self, *expects: type[T_Ref]) -> T_Ref:
		"""期待する型と同種ならキャスト

		Args:
			*expects (type[T_Ref]): 期待する型
		Returns:
			T_Ref: インスタンス
		Raises:
			LogicError: 継承関係が無い型を指定 XXX 出力する例外は要件等
		"""
		return self.__new_raw_proxy.one_of(*expects)

	@override
	def __eq__(self, other: object) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (object): 比較対象
		Returns:
			bool: True = 同じ
		"""
		return self.__new_raw_proxy.__eq__(other)

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return self.__new_raw_proxy.__repr__()

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return self.__new_raw_proxy.__str__()
