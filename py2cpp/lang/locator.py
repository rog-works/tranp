from typing import Callable, Protocol, TypeAlias, TypeVar

T_Inst = TypeVar('T_Inst')
T_Injector: TypeAlias = type[T_Inst] | Callable[..., T_Inst]
T_Curried = TypeVar('T_Curried', bound=Callable)

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

	def curry(self, factory: T_Injector, expect: type[T_Curried]) -> T_Curried:
		"""指定のファクトリーをカリー化した関数を返却

		Args:
			factory (T_Injector): ファクトリー(関数/メソッド/クラス)
			expect (type[T_Curried]): 期待するカリー化関数のシグネチャー
		Returns:
			T_Curried: カリー化関数
		"""
		...
