from collections.abc import Callable
from typing import Any, Protocol, TypeAlias, TypeVar

T_Inst = TypeVar('T_Inst')

Injector: TypeAlias = type[T_Inst] | Callable[..., T_Inst]


class Locator(Protocol):
	"""ロケーター。シンボルからインスタンスを解決"""

	def can_resolve(self, symbol: type) -> bool:
		"""シンボルが解決できるか判定

		Args:
			symbol: シンボル
		Returns:
			True = 解決できる
		"""
		...

	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol: シンボル
		Returns:
			インスタンス
		Raises:
			ValueError: 未登録のシンボルを指定
		"""
		...

	def invoke(self, factory: Injector[T_Inst], *remain_args: Any) -> T_Inst:
		"""ファクトリーを代替実行し、インスタンスを生成

		Args:
			factory: ファクトリー(関数/メソッド/クラス)
			*remain_args (Any): 残りの位置引数
		Returns:
			生成したインスタンス
		Note:
			* ロケーターが解決可能なシンボルをファクトリーの引数リストの前方から省略していき、解決不能な引数を残りの位置引数として受け取る
			* このメソッドを通して生成したインスタンスはキャッシュされず、毎回生成される
		"""
		...


class Invoker(Protocol):
	"""ファクトリー関数プロトコル"""

	def __call__(self, factory: Injector[T_Inst], *remain_args: Any) -> T_Inst:
		"""Note: @see Locator.invoke"""
		...
