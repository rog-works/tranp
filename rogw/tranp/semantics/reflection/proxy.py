from typing import Callable, Iterator

from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.interface import ISymbolProxy, IReflection, T_Ref
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
	def types(self) -> defs.ClassDef:
		"""ClassDef: 型を表すノード"""
		return self.__new_raw_proxy.types

	@property
	@implements
	def decl(self) -> defs.DeclAll:
		"""DeclAll: 定義元のノード"""
		return self.__new_raw_proxy.decl

	@property
	@implements
	def node(self) -> Node:
		"""Node: ノード"""
		return self.__new_raw_proxy.node

	@property
	@implements
	def origin(self) -> IReflection:
		"""IReflection: 型のシンボル"""
		return self.__new_raw_proxy.origin

	@property
	@implements
	def via(self) -> IReflection:
		"""IReflection: スタックシンボル"""
		return self.__new_raw_proxy.via

	@property
	@implements
	def context(self) -> IReflection:
		"""IReflection: コンテキストを取得 Raises: SemanticsLogicError: コンテキストが無い状態で使用"""
		return self.__new_raw_proxy.context

	@property
	@implements
	def attrs(self) -> list[IReflection]:
		"""list[IReflection]: 属性シンボルリスト"""
		return self.__new_raw_proxy.attrs

	@implements
	def declare(self, decl: defs.DeclVars, origin: 'IReflection | None' = None) -> 'IReflection':
		"""定義ノードをスタック

		Args:
			decl (DeclVars): 定義元のノード
		Returns:
			IReflection: リフレクション
		"""
		return self.__new_raw_proxy.declare(decl)

	@implements
	def stack_by(self, node: Node) -> 'IReflection':
		"""ノードをスタック

		Args:
			node (Node): ノード
		Returns:
			IReflection: リフレクション
		"""
		return self.__new_raw_proxy.stack_by(node)

	@implements
	def stack_by_self(self) -> 'IReflection':
		"""自身を参照としてスタック

		Returns:
			IReflection: リフレクション
		"""
		return self.__new_raw_proxy.stack_by_self()

	@implements
	def to(self, node: Node, origin: 'IReflection') -> 'IReflection':
		"""ノードをスタックし、型のシンボルを移行

		Args:
			node (Node): ノード
			origin (IReflection): 型のシンボル
		Returns:
			IReflection: リフレクション
		"""
		return self.__new_raw_proxy.to(node, origin)

	@property
	@implements
	def shorthand(self) -> str:
		"""str: オブジェクトの短縮表記"""
		return self.__new_raw_proxy.shorthand

	@implements
	def stacktrace(self) -> Iterator[IReflection]:
		"""参照元を辿るイテレーターを取得

		Returns:
			Iterator[IReflection]: イテレーター
		"""
		return self.__new_raw_proxy.stacktrace()

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
