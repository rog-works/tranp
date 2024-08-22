from rogw.tranp.semantics.reflection.interface import IReflection
import rogw.tranp.syntax.node.definition as defs


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
