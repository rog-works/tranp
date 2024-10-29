from typing import Iterator, Literal, Self, cast, override

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import implements
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
	def actualize(self: Self, *targets: Literal['nullable', 'self', 'type', 'alt_class'], instance: IReflection) -> Self:
		"""プロクシー型から実体型を解決。元々実体型である場合はそのまま返却

		Args:
			*targets (Literal['nullable', 'self', 'type', 'alt_class']): 処理対象。省略時は全てが対象
			instance (IReflection): シンボル ※Traitsから暗黙的に入力される
		Returns:
			Self: シンボル
		Note:
			### 変換対象
			* Union型: Class | None
			* Self型: type<Self>, Self
			* type型: type<Class>
			* TypeAlias型: T<Class>
			### Selfの妥当性
			* XXX 実質的に具象クラスはReflectionのみであり、アンパック後も型は変化しない
			* XXX リフレクション拡張の型(=Self)として継続して利用できる方が効率が良い
		"""
		actualizers = {
			'nullable': self._actualize_nullable,
			'self': self._actualize_self,
			'type': self._actualize_type,
			'alt_class': self._actualize_alt_class,
		}
		all_on = len(targets) == 0
		actual = instance
		changed = False
		for key, actualizer in actualizers.items():
			if all_on or key in targets:
				in_changed, actual = actualizer(actual)
				changed |= in_changed

		if changed:
			return cast(Self, instance.to(instance.node, actual))
		else:
			return cast(Self, actual)

	def _actualize_nullable(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""Nullable型から実体型を解決

		Args:
			symbol (IReflection): シンボル
		Returns:
			tuple[bool, IReflection]: 解決可否, シンボル
		Note:
			Class | None -> Class
		"""
		if self.reflections.type_is(symbol.types, classes.Union) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.type_is(symbol.attrs[0].types, None)
			is_1_null = self.reflections.type_is(symbol.attrs[1].types, None)
			if is_0_null != is_1_null:
				return True, symbol.attrs[1 if is_0_null else 0]

		return False, symbol

	def _actualize_self(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""Self型から実体型を解決

		Args:
			symbol (IReflection): シンボル
		Returns:
			tuple[bool, IReflection]: 解決可否, シンボル
		Note:
			type<Self> -> type<Class>
			Self -> Class
			FIXME Selfに直接依存するのはNG
		"""
		if isinstance(symbol.node, defs.ClassRef) and isinstance(symbol.attrs[0].types, defs.TemplateClass) and symbol.attrs[0].types.domain_name == Self.__name__:
			return True, self.reflections.from_standard(type).stack().extends(self.reflections.resolve(symbol.node.class_types.as_a(defs.Class)))
		elif isinstance(symbol.node, defs.ThisRef) and isinstance(symbol.types, defs.TemplateClass) and symbol.types.domain_name == Self.__name__:
			return True, self.reflections.resolve(symbol.node.class_types.as_a(defs.Class))

		return False, symbol

	def _actualize_type(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""type型から実体型を解決

		Args:
			symbol (IReflection): シンボル
		Returns:
			tuple[bool, IReflection]: 解決可否, シンボル
		Note:
			type<Class> -> Class
		"""
		if isinstance(symbol.decl, (defs.DeclClasses, defs.DeclVars)) and self.reflections.type_is(symbol.types, type):
			return True, symbol.attrs[0]
		else:
			return False, symbol

	def _actualize_alt_class(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""AltClass型から実体型を解決

		Args:
			symbol (IReflection): シンボル
		Returns:
			tuple[bool, IReflection]: 解決可否, シンボル
		Note:
			T<Class> -> Class
		"""
		if isinstance(symbol.types, defs.AltClass):
			return True, symbol.attrs[0]
		else:
			return False, symbol


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
		if value in parameter_types:
			return method.returns(value)

		if not isinstance(value.types, defs.Class):
			return None

		for inherit in value.types.inherits:
			inherit_symbol = self.reflections.resolve(inherit)
			if inherit_symbol in parameter_types:
				return method.returns(inherit_symbol)

		return None

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
		return self.reflections.resolve_property(instance.types, prop)

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
		if function_helper.is_a(templates.ClassMethod):
			# XXX コンテキストは常に実体型になるためtype<Class>の形式に変換
			return function_helper.parameter(index, self.reflections.from_standard(type).stack().extends(instance.context), argument)
		elif function_helper.is_a(templates.Method):
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
		if function_helper.is_a(templates.ClassMethod):
			# XXX コンテキストは常に実体型になるためtype<Class>の形式に変換
			return function_helper.returns(self.reflections.from_standard(type).stack().extends(instance.context), *arguments)
		elif function_helper.is_a(templates.Method):
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
