from typing import Iterator, Self, cast

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.errors import UnresolvedSymbolError
from rogw.tranp.semantics.reflection.base import IReflection, Trait
import rogw.tranp.semantics.reflection.definitions as refs
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interfaces import IConvertion, IFunction, IIterator, IObject
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		list[type[Trait]]: トレイトのクラスリスト
	"""
	return [
		ConvertionTrait,
		ObjectTrait,
		IteratorTrait,
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


class ConvertionTrait(TraitImpl, IConvertion):
	"""トレイト実装(変換)"""

	def is_a(self, standard_type: type[Standards] | None, symbol: IReflection) -> bool:
		"""シンボルの型を判定

		Args:
			standard_type (type[Standards] | None): 標準タイプ
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			bool: True = 指定の型と一致
		"""
		return self.reflections.is_a(symbol, standard_type)

	def actualize(self: Self, symbol: IReflection) -> Self:
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
		"""
		actual = self._unpack_nullable(symbol)
		actual = self._unpack_alt_class(actual)
		actual = self._unpack_type(actual)
		return cast(Self, actual)

	def _unpack_nullable(self, symbol: IReflection) -> IReflection:
		"""Nullable型をアンパック

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: シンボル
		Note:
			対象: Class | None
		"""
		if self.reflections.is_a(symbol, classes.Union) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.is_a(symbol.attrs[0], None)
			is_1_null = self.reflections.is_a(symbol.attrs[1], None)
			if is_0_null != is_1_null:
				return symbol.attrs[1 if is_0_null else 0]

		return symbol

	def _unpack_alt_class(self, symbol: IReflection) -> IReflection:
		"""AltClass型をアンパック

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: シンボル
		Note:
			対象: T<Class>
		"""
		return symbol.attrs[0] if isinstance(symbol.types, defs.AltClass) else symbol

	def _unpack_type(self, symbol: IReflection) -> IReflection:
		"""type型をアンパック

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: シンボル
		Note:
			対象: type<T> -> T
		"""
		return symbol.attrs[0] if isinstance(symbol.decl, defs.Class) and self.reflections.is_a(symbol, type) else symbol


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

	@implements
	def constructor(self, symbol: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return symbol.to(symbol.types, self.reflections.type_of_constructor(symbol.types.as_a(defs.Class)))


class IteratorTrait(TraitImpl, IIterator):
	"""トレイト実装(イテレーター)"""

	def iterates(self, symbol: IReflection) -> IReflection:
		"""イテレーターの結果を解決

		Args:
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		method = symbol.to(symbol.types, self._resolve_method(symbol))
		iterates = method.impl(refs.Function).returns()
		# メソッド毎の返却値の違いを吸収
		# iterator: () -> T
		# iterable: () -> Iterator<T>
		return iterates.attrs[0] if self.reflections.is_a(iterates, cast(type, Iterator)) else iterates

	def _resolve_method(self, symbol: IReflection) -> IReflection:
		"""イテレーターのメソッドを解決

		Args:
			symbol (IReflection): シンボル
		Returns:
			IReflection: シンボル
		"""
		try:
			return self.reflections.resolve(symbol.types, symbol.types.operations.iterator)
		except UnresolvedSymbolError:
			return self.reflections.resolve(symbol.types, symbol.types.operations.iterable)


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
			schema = {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.context}
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
