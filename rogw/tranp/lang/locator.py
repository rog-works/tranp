from typing import Any, Callable, Protocol, TypeAlias, TypeVar

T_Inst = TypeVar('T_Inst')
T_Curried = TypeVar('T_Curried', bound=Callable)

Injector: TypeAlias = type[T_Inst] | Callable[..., T_Inst]


class Locator(Protocol):
	"""ロケーター。シンボルからインスタンスを解決"""

	def can_resolve(self, symbol: type) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol (type): シンボル
		Returns:
			bool: True = 解決できる
		"""
		...

	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
		Raises:
			ValueError: 未登録のシンボルを指定
		"""
		...

	def currying(self, factory: Injector[Any], expect: type[T_Curried]) -> T_Curried:
		"""指定のファクトリーをカリー化して返却

		Args:
			factory (Injector[Any]): ファクトリー(関数/メソッド/クラス)
			expect (type[T_Curried]): カリー化後に期待する関数シグネチャー
		Returns:
			T_Curried: カリー化後の関数
		Note:
			ロケーターが解決可能なシンボルを引数リストの前方から省略していき、
			解決不能なシンボルを残した関数が返却値となる
		"""
		...

	def invoke(self, factory: Injector[T_Inst]) -> T_Inst:
		"""ファクトリーを代替実行し、インスタンスを生成

		Args:
			factory (Injector[T_Inst]): ファクトリー(関数/メソッド/クラス)
		Returns:
			T_Inst: 生成したインスタンス
		Note:
			このメソッドを通して生成したインスタンスはキャッシュされず、毎回生成される
		"""
		...


class Currying(Protocol):
	"""カリー化関数プロトコル"""

	def __call__(self, factory: Injector[Any], expect: type[T_Curried]) -> T_Curried:
		"""Note: @see Locator.currying"""
		...
