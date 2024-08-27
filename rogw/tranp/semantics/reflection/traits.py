from typing import Iterator, Literal, Self, cast

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import implements, override
from rogw.tranp.lang.trait import Trait
from rogw.tranp.semantics.errors import UnresolvedSymbolError
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interfaces import IConvertion, IFunction, IIterator, IOperation, IProperties
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
		OperationTrait,
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

	@implements
	def type_is(self, standard_type: type[Standards] | None, instance: IReflection) -> bool:
		"""シンボルの型を判定

		Args:
			standard_type (type[Standards] | None): 標準タイプ
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			bool: True = 指定の型と一致
		"""
		return self.reflections.type_is(instance.types, standard_type)

	@implements
	def actualize(self: Self, *targets: Literal['nullable', 'alt_class', 'type'], instance: IReflection) -> Self:
		"""プロクシー型(Union/TypeAlias/type)による階層化を解除し、実体型を取得。元々実体型である場合はそのまま返却

		Args:
			*targets (Literal['nullable', 'alt_class', 'type']): 処理対象。省略時は全てが対象
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
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
		actual = instance
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
		if self.reflections.type_is(symbol.types, classes.Union) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.type_is(symbol.attrs[0].types, None)
			is_1_null = self.reflections.type_is(symbol.attrs[1].types, None)
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
		return symbol.attrs[0] if isinstance(symbol.decl, defs.Class) and self.reflections.type_is(symbol.types, type) else symbol


class OperationTrait(TraitImpl, IOperation):
	"""トレイト実装(演算)"""

	@implements
	def try_operation(self, operator: defs.Terminal, value: IReflection, instance: IReflection) -> IReflection | None:
		"""演算を試行し、結果を返却。該当する演算メソッドが存在しない場合はNoneを返却

		Args:
			operator (Terminal): 演算子ノード
			value (IReflection): 値のシンボル
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		method = self._find_method(instance, instance.types.operations.operation_by(operator.tokens))
		if method is None:
			return None

		# XXX 算術演算以外(比較/ビット演算)は返却型が左右で必ず同じであり、戻り値の型の選別が不要であるため省略する
		if not instance.types.operations.arthmetical(operator.tokens):
			return method.returns(value)

		parameter = method.parameter_at(0, value)
		parameter_types = parameter.attrs if parameter.impl(refs.Object).type_is(classes.Union) else [parameter]
		if value not in parameter_types:
			return None

		return method.returns(value)

	def _find_method(self, symbol: IReflection, method_name: str) -> refs.Function | None:
		"""演算用のメソッドを検索。存在しない場合はNoneを返却

		Args:
			symbol (IReflection): シンボル
			method_name (str): メソッド名
		Returns:
			Function | None: シンボル
		"""
		try:
			return symbol.to(symbol.types, self.reflections.resolve(symbol.types, method_name)).impl(refs.Function)
		except UnresolvedSymbolError:
			return None


class PropertiesTrait(TraitImpl, IProperties):
	"""トレイト実装(プロパティー管理)"""

	@implements
	def prop_of(self, prop: defs.Var, instance: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop (Var): 変数参照ノード
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return instance.to(prop, self.reflections.resolve_property(instance.types, prop))

	@implements
	def constructor(self, instance: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		return self.reflections.resolve_constructor(instance.types.as_a(defs.Class))


class IteratorTrait(TraitImpl, IIterator):
	"""トレイト実装(イテレーター)"""

	@implements
	def iterates(self, instance: IReflection) -> IReflection:
		"""イテレーターの結果を解決

		Args:
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		method = instance.to(instance.types, self._resolve_method(instance))
		iterates = method.impl(refs.Function).returns()
		# メソッド毎の返却値の違いを吸収
		# __iter__() -> T
		# __next__() -> Iterator<T>
		return iterates.attrs[0] if self.reflections.type_is(iterates.types, cast(type, Iterator)) else iterates

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
	def parameter_at(self, index: int, argument: IReflection, instance: IReflection) -> IReflection:
		"""引数の実体型を解決

		Args:
			index (int): 引数のインデックス
			argument (IReflection): 引数の実体
			**reserved (IReflection): シンボル入力用の予約枠 ※実引数は指定しない
		Returns:
			IReflection: シンボル
		"""
		function_helper = self._build_helper(instance)
		if function_helper.is_a(templates.Method):
			return function_helper.parameter(index, instance.context, argument)
		else:
			return function_helper.parameter(index, argument)

	@implements
	def returns(self, *arguments: IReflection, instance: IReflection) -> IReflection:
		"""戻り値の実体型を解決

		Args:
			*arguments (IReflection): 引数リスト
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			IReflection: シンボル
		"""
		function_helper = self._build_helper(instance)
		if function_helper.is_a(templates.Method):
			return function_helper.returns(instance.context, *arguments)
		else:
			return function_helper.returns(*arguments)

	@implements
	def function_templates(self, instance: IReflection) -> list[defs.TemplateClass]:
		"""保有するテンプレート型ノードを取得

		Args:
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			list[TemplateClass]: テンプレート型ノードのリスト
		Note:
			XXX クラスにも同様の属性があるため、IGenericなどに分離を検討
		"""
		return self._build_helper(instance).templates()

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
