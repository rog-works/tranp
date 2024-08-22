from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.extensions import IFunction, IObject
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interface import IReflection, Trait
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


class TraitBase(Trait, IObject):
	"""トレイト実装(基底)"""

	@override
	def __init__(self, reflections: Reflections, symbol: IReflection) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
			symbol (IReflection): 拡張対象のインスタンス
		"""
		self.reflections = reflections
		self.symbol = symbol


class ObjectTrait(TraitBase, IObject):
	"""トレイト実装(オブジェクト)"""

	@implements
	def prop_of(self, prop: defs.Var) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
		Returns:
			IReflection: シンボル
		"""
		return self.symbol.to(prop, self.reflections.type_of_property(self.symbol.types, prop))


class FunctionTrait(TraitBase, IFunction):
	"""トレイト実装(ファンクション)"""

	@implements
	def returns(self, *arguments: IReflection) -> IReflection:
		"""戻り値の実体型を解決

		Args:
			*arguments (IReflection): 引数リスト
		Returns:
			IReflection: シンボル
		"""
		if self.symbol.types.is_a(defs.Constructor):
			schema = {'klass': self.symbol.attrs[0], 'parameters': self.symbol.attrs[1:-1], 'returns': self.symbol.attrs[0]}
			function_helper = templates.HelperBuilder(self.symbol).schema(lambda: schema).build(templates.Constructor)
			return function_helper.returns(self.symbol.context, *arguments)
		elif self.symbol.types.is_a(defs.Method, defs.ClassMethod):
			schema = {'klass': self.symbol.attrs[0], 'parameters': self.symbol.attrs[1:-1], 'returns': self.symbol.attrs[-1]}
			function_helper = templates.HelperBuilder(self.symbol).schema(lambda: schema).build(templates.Method)
			return function_helper.returns(self.symbol.context, *arguments)
		else:
			schema = {'parameters': self.symbol.attrs[:-1], 'returns': self.symbol.attrs[-1]}
			function_helper = templates.HelperBuilder(self.symbol).schema(lambda: schema).build(templates.Function)
			return function_helper.returns(*arguments)


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		list[type[Trait]]: トレイトのクラスリスト
	"""
	return [
		ObjectTrait,
		FunctionTrait,
	]
