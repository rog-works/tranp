from typing import Any, Protocol, Self

from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.syntax.node.definition as defs


class IExample(Protocol):
	"""拡張インターフェイス(プロトコル)"""

	def __call__(self, *args: Any, **injected: IReflection) -> Any:
		"""メソッドの共通シグネチャー

		Args:
			*args (Any): 実引数を受け取る位置引数。数も型も任意であり、省略も可
			**injected (IReflection): 実引数は受け取らないキーワード引数。型はIReflection固定。Traitsからシンボルを入力するために必須 @see Traits.get
		"""
		...


class IConvertion:
	"""拡張インターフェイス(変換)"""

	def is_a(self, standard_type: type[Standards] | None, **injected: IReflection) -> bool:
		"""シンボルの型を判定

		Args:
			standard_type (type[Standards] | None): 標準タイプ
			**injected (IReflection): シンボル入力用のキーワード引数 ※インターフェイス上は無視して問題ない
		Returns:
			bool: True = 指定の型と一致
		"""
		...

	def actualize(self: Self, **injected: IReflection) -> Self:
		"""プロクシー型(Union/TypeAlias/type)による階層化を解除し、実体型を取得。元々実体型である場合はそのまま返却

		Args:
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			Self: シンボル
		Note:
			### 変換対象
			* Class | None
			* T<Class>
			* type<Class>
			### Selfの妥当性
			* XXX 実質的に具象クラスはReflectionのみであり、アンパック後も型は変化しない
			* XXX リフレクション拡張の型(=Self)として継続して利用できる方が効率が良い
		"""
		...


class IObject:
	"""拡張インターフェイス(オブジェクト)"""

	def prop_of(self, prop: defs.Var, **injected: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
			**injected (IReflection): シンボル入力用のキーワード引数 ※インターフェイス上は無視して問題ない
		Returns:
			IReflection: シンボル
		"""
		...

	def constructor(self, **injected: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			**injected (IReflection): シンボル入力用のキーワード引数 ※インターフェイス上は無視して問題ない
		Returns:
			IReflection: シンボル
		"""
		...


class IIterator:
	"""拡張インターフェイス(イテレーター)"""

	def iterates(self, **injected: IReflection) -> IReflection:
		"""イテレーターの結果を解決

		Args:
			**injected (IReflection): シンボル入力用のキーワード引数 ※インターフェイス上は無視して問題ない
		Returns:
			IReflection: シンボル
		"""
		...


class IFunction:
	"""拡張インターフェイス(ファンクション)"""

	def returns(self, *arguments: IReflection, **injected: IReflection) -> IReflection:
		"""戻り値の実体型を解決

		Args:
			*arguments (IReflection): 引数リスト
			**injected (IReflection): シンボル入力用のキーワード引数 ※インターフェイス上は無視して問題ない
		Returns:
			IReflection: シンボル
		"""
		...
