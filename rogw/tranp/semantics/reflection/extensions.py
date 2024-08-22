from rogw.tranp.semantics.reflection.interface import IReflection
import rogw.tranp.syntax.node.definition as defs


class IObject:
	"""拡張インターフェイス(オブジェクト)"""

	def prop_of(self, prop: defs.Var) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
		Returns:
			IReflection: シンボル
		"""
		...
