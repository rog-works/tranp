from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.extensions import IObject
from rogw.tranp.semantics.reflection.interface import IReflection, Trait
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


class ObjectTrait(Trait, IObject):
	"""トレイト(オブジェクト)"""

	@override
	def __init__(self, reflections: Reflections, symbol: IReflection) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			symbol (IReflection): 拡張対象のインスタンス
		"""
		self.reflections = reflections
		self.symbol = symbol

	@implements
	def prop_of(self, prop: defs.Var) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
		Returns:
			IReflection: シンボル
		"""
		return self.reflections.type_of_property(self.symbol.types, prop)


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		list[type[Trait]]: トレイトのクラスリスト
	"""
	return [
		ObjectTrait,
	]
