from collections.abc import Callable
from typing import TypeVar, TypeVarTuple

T = TypeVar('T')
T_Func = TypeVar('T_Func', bound=Callable)
T_Ret = TypeVar('T_Ret')
T_Args = TypeVarTuple('T_Args')


def c_func_ref(func: T_Func) -> T_Func:
	"""関数オブジェクトをC++用の関数ポインターとしての解釈を付与

	Args:
		func: 関数オブジェクト
	Returns:
		関数オブジェクト (C++では関数ポインター)
	Examples:
		```python
		class Delegate(Generic[*T_Args, T_Ret]):
			def bind(self, receiver: T, func: Callable[[T, *T_Args], T_Ret]) -> None: ...

		class A:
			def __init__(self)
				self.delegete = Delegate[int, None]()
				self.delegate.bind(self, c_func_ref(A.callback))

			def callback(self, n: int) -> None: ...
		```
	"""
	return func


def c_func_invoke(receiver: T, func: Callable[[T, *T_Args], T_Ret], *args: *T_Args) -> T_Ret:
	"""関数の代替呼び出し

	Args:
		receiver: メソッドレシーバー
		func: 関数オブジェクト
		*args: 引数リスト
	Returns:
		戻り値
	Note:
		```
		* XXX C++の関数ポインターは変数単体とコレクション型で変数宣言のシグネチャーが異なる
		* XXX 実装の煩雑さを回避するため、コレクション型のみ利用すると言う前提で扱い、変数単体は非対応とする
		* XXX また、TypeVarTupleのテンプレート展開が不完全であるため、c_func_invokeの戻り値の型はMoveAssignで推論できない点に注意
		```
	Examples:
		```python
		class A:
			def func_a(self) -> int: ...
			def func_b(self) -> int: ...

		func_map = {'a': c_func_ref(A.func_a), 'b': c_func_ref(A.func_b)}
		n: int = c_func_invoke(A(), func_map['a'])
		```
	"""
	return func(receiver, *args)
