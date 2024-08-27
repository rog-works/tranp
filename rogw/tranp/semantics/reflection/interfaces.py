from typing import Any, Literal, Protocol, Self

from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.syntax.node.definition as defs


class IExample(Protocol):
	"""拡張インターフェイス(プロトコル)"""

	def __call__(self, *args: Any, **reserved: IReflection) -> Any:
		"""メソッドの共通シグネチャー

		Args:
			*args (Any): 実引数を受け取る位置引数。数も型も任意であり、省略も可
			**reserved  (IReflection): 実引数は受け取らないキーワード引数。型はIReflection固定。Traitsからシンボルを入力するために定義上必須 @see Traits.get
		"""
		...


class IConvertion:
	"""拡張インターフェイス(変換)"""

	def type_is(self, standard_type: type[Standards] | None, **reserved: IReflection) -> bool:
		"""シンボルの型を判定

		Args:
			standard_type (type[Standards] | None): 標準タイプ
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			bool: True = 指定の型と一致
		"""
		...

	def actualize(self: Self, *targets: Literal['nullable', 'alt_class', 'type', 'self'], **reserved: IReflection) -> Self:
		"""プロクシー型から実体型を解決。元々実体型である場合はそのまま返却

		Args:
			*targets (Literal['nullable', 'alt_class', 'type']): 処理対象。省略時は全てが対象
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			Self: シンボル
		Note:
			### 変換対象
			* Union型: Class | None
			* TypeAlias型: T<Class>
			* type型: type<Class>
			* Self型: Self
			### Selfの妥当性
			* XXX 実質的に具象クラスはReflectionのみであり、アンパック後も型は変化しない
			* XXX リフレクション拡張の型(=Self)として継続して利用できる方が効率が良い
		"""
		...


class IOperation:
	"""拡張インターフェイス(演算)"""

	def try_operation(self, operator: defs.Terminal, value: IReflection, **reserved: IReflection) -> IReflection | None:
		"""演算を試行し、結果を返却。該当する演算メソッドが存在しない場合はNoneを返却

		Args:
			operator (Terminal): 演算子ノード
			value (IReflection): 値のシンボル
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...


class IProperties:
	"""拡張インターフェイス(プロパティー管理)"""

	def prop_of(self, prop: defs.Var, **reserved: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...

	def constructor(self, **reserved: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...


class IIterator:
	"""拡張インターフェイス(イテレーター)"""

	def iterates(self, **reserved: IReflection) -> IReflection:
		"""イテレーターの結果を解決

		Args:
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...


class IFunction:
	"""拡張インターフェイス(ファンクション)"""

	def parameter_at(self, index: int, argument: IReflection, **reserved: IReflection) -> IReflection:
		"""引数の実体型を解決

		Args:
			index (int): 引数のインデックス
			argument (IReflection): 引数の実体
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...

	def returns(self, *arguments: IReflection, **reserved: IReflection) -> IReflection:
		"""戻り値の実体型を解決

		Args:
			*arguments (IReflection): 引数リスト
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		...

	def function_templates(self, **reserved: IReflection) -> list[defs.TemplateClass]:
		"""保有するテンプレート型ノードを取得

		Args:
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			list[TemplateClass]: テンプレート型ノードのリスト
		Note:
			XXX クラスにも同様の属性があるため、IGenericなどに分離を検討
		"""
		...


class Object(IReflection, IConvertion, IOperation, IProperties):
	"""リフレクション拡張型(オブジェクト)"""


class Iterator(IReflection, IIterator):
	"""リフレクション拡張型(イテレーター)"""


class Function(IReflection, IFunction):
	"""リフレクション拡張型(ファンクション)"""
