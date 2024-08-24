from typing import Iterator, Literal, Self, cast

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.semantics.errors import UnresolvedSymbolError
from rogw.tranp.semantics.reflection.base import IReflection, Trait
import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interfaces import IConvertion, IFunction, IIterator, IProperties
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		list[type[Trait]]: トレイトのクラスリスト
	"""
	return [
		ConvertionTrait,
		PropertiesTrait,
		IteratorTrait,
		FunctionTrait,
	]


class TraitImpl(Trait):
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

	def actualize(self: Self, *targets: Literal['nullable', 'alt_class', 'type'], symbol: IReflection) -> Self:
		"""プロクシー型(Union/TypeAlias/type)による階層化を解除し、実体型を取得。元々実体型である場合はそのまま返却

		Args:
			*targets (Literal['nullable', 'alt_class', 'type']): 処理対象。省略時は全てが対象
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
		actual = symbol
		actual = self._unpack_nullable(actual) if len(targets) == 0 or 'nullable' in targets else actual
		actual = self._unpack_alt_class(actual) if len(targets) == 0 or 'alt_class' in targets else actual
		actual = self._unpack_type(actual) if len(targets) == 0 or 'type' in targets else actual
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


class PropertiesTrait(TraitImpl, IProperties):
	"""トレイト実装(プロパティー管理)"""

	@implements
	def prop_of(self, prop: defs.Var, symbol: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return symbol.to(prop, self.reflections.resolve_property(symbol.types, prop))

	@implements
	def constructor(self, symbol: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return symbol.to(symbol.types, self.reflections.resolve_constructor(symbol.types.as_a(defs.Class)))


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
		# __iter__() -> T
		# __next__() -> Iterator<T>
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
		function_helper = self._build_helper(symbol)
		if function_helper.is_a(templates.Method):
			return function_helper.returns(symbol.context, *arguments)
		else:
			return function_helper.returns(*arguments)

	def function_templates(self, symbol: IReflection) -> list[defs.TemplateClass]:
		"""保有するテンプレート型ノードを取得

		Args:
			symbol (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			list[TemplateClass]: テンプレート型ノードのリスト
		Note:
			XXX クラスにも同様の属性があるため、IGenericなどに分離を検討
		"""
		return self._build_helper(symbol).templates()

	def _build_helper(self, symbol: IReflection) -> templates.Function:
		"""ヘルパー(ファンクション)を生成

		Args:
			symbol (IReflection): シンボル
		Returns:
			Function: ヘルパー(ファンクション)
		"""
		return templates.HelperBuilder(symbol).schema(lambda: self._build_schema(symbol)).build(templates.Function)

	def _build_schema(self, symbol: IReflection) -> templates.InjectSchemata:
		"""ヘルパー用スキーマを生成

		Args:
			symbol (IReflection): シンボル
		Returns:
			InjectSchema: ヘルパー用スキーマ
		"""
		if symbol.types.is_a(defs.Constructor):
			return {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.context}
		elif symbol.types.is_a(defs.Method, defs.ClassMethod):
			return {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.attrs[-1]}
		else:
			return {'parameters': symbol.attrs[:-1], 'returns': symbol.attrs[-1]}
