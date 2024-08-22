from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.reflection.base import IReflection, Trait
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interfaces import IFunction, IObject
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		list[type[Trait]]: トレイトのクラスリスト
	"""
	return [
		ObjectTrait,
		FunctionTrait,
	]


class TraitImpl(Trait, IObject):
	"""トレイト実装(基底)"""

	@override
	def __init__(self, reflections: Reflections) -> None:
		"""インスタンスを生成

		Args:
			reflections (Reflections): シンボルリゾルバー @inject
		"""
		self.reflections = reflections


class ObjectTrait(TraitImpl, IObject):
	"""トレイト実装(オブジェクト)"""

	@implements
	def prop_of(self, prop: defs.Var, symbol: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return symbol.to(prop, self.reflections.type_of_property(symbol.types, prop))


class FunctionTrait(TraitImpl, IFunction):
	"""トレイト実装(ファンクション)"""

	@implements
	def returns(self, *arguments: IReflection, symbol: IReflection) -> IReflection:
		"""戻り値の実体型を解決

		Args:
			*arguments (IReflection): 引数リスト
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		if symbol.types.is_a(defs.Constructor):
			schema = {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.attrs[0]}
			function_helper = templates.HelperBuilder(symbol).schema(lambda: schema).build(templates.Constructor)
			return function_helper.returns(symbol.context, *arguments)
		elif symbol.types.is_a(defs.Method, defs.ClassMethod):
			schema = {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.attrs[-1]}
			function_helper = templates.HelperBuilder(symbol).schema(lambda: schema).build(templates.Method)
			return function_helper.returns(symbol.context, *arguments)
		else:
			schema = {'parameters': symbol.attrs[:-1], 'returns': symbol.attrs[-1]}
			function_helper = templates.HelperBuilder(symbol).schema(lambda: schema).build(templates.Function)
			return function_helper.returns(*arguments)
