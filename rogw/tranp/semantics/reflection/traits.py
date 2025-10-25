from collections.abc import Iterator
from typing import Literal, Self, cast, override

from rogw.tranp.compatible.python.types import Standards, Union
from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import implements
from rogw.tranp.lang.trait import Trait
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.semantics.reflection.helper.template as templates
from rogw.tranp.semantics.reflection.interfaces import IConvertion, IFunction, IIterator, IOperation, IProperties
from rogw.tranp.semantics.reflections import Reflections
import rogw.tranp.syntax.node.definition as defs


def export_classes() -> list[type[Trait]]:
	"""公開トレイトのクラスリストを取得

	Returns:
		トレイトのクラスリスト
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
			reflections: シンボルリゾルバー @inject
		"""
		self.reflections = reflections


class ConvertionTrait(TraitImpl, IConvertion):
	"""トレイト実装(変換)"""

	@implements
	def type_is(self, standard_type: type[Standards] | None, instance: IReflection) -> bool:
		"""シンボルの型を判定

		Args:
			standard_type: 標準タイプ
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			True = 指定の型と一致
		"""
		return self.reflections.type_is(instance.types, standard_type)

	@implements
	def actualize(self: Self, *targets: Literal['nullable', 'self', 'type', 'template', 'alt'], instance: IReflection) -> Self:
		"""プロクシー型から実体型を解決。元々実体型である場合はそのまま返却

		Args:
			*targets: 処理対象。省略時は全てが対象
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
		Note:
			```
			### 変換対象
			* Union型: Class | None
			* Self型: type<Self>, Self
			* type型: type<Class>
			* TemplateClass型: T
			* AltClass型: T<Class>
			### Selfの妥当性
			* XXX 実質的に具象クラスはReflectionのみであり、アンパック後も型は変化しない
			* XXX リフレクション拡張の型(=Self)として継続して利用できる方が効率が良い
			```
		"""
		actualizers = {
			'nullable': self._actualize_nullable,
			'self': self._actualize_self,
			'type': self._actualize_type,
			'template': self._actualize_template,
			'alt': self._actualize_alt,
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
			symbol: シンボル
		Returns:
			解決可否, シンボル
		Note:
			Class | None -> Class
		"""
		if self.reflections.type_is(symbol.types, Union) and len(symbol.attrs) == 2:
			is_0_null = self.reflections.type_is(symbol.attrs[0].types, None)
			is_1_null = self.reflections.type_is(symbol.attrs[1].types, None)
			if is_0_null != is_1_null:
				return True, symbol.attrs[1 if is_0_null else 0]

		return False, symbol

	def _actualize_self(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""Self型から実体型を解決

		Args:
			symbol: シンボル
		Returns:
			解決可否, シンボル
		Note:
			```
			* type<Self> -> type<Class>
			* Self -> Class
			FIXME Selfに直接依存するのはNG
			```
		"""
		if isinstance(symbol.node, defs.ClassRef) and isinstance(symbol.attrs[0].types, defs.TemplateClass) and symbol.attrs[0].types.domain_name == Self.__name__:
			return True, self.reflections.from_standard(type).stack().extends(self.reflections.resolve(symbol.node.class_types.as_a(defs.Class)))
		elif isinstance(symbol.node, defs.ThisRef) and isinstance(symbol.types, defs.TemplateClass) and symbol.types.domain_name == Self.__name__:
			return True, self.reflections.resolve(symbol.node.class_types.as_a(defs.Class))

		return False, symbol

	def _actualize_type(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""type型から実体型を解決

		Args:
			symbol: シンボル
		Returns:
			解決可否, シンボル
		Note:
			type<Class> -> Class
		"""
		if isinstance(symbol.decl, (defs.DeclClasses, defs.DeclVars)) and self.reflections.type_is(symbol.types, type):
			return True, symbol.attrs[0]
		else:
			return False, symbol

	def _actualize_template(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""TemplateClass型から実体型を解決

		Args:
			symbol: シンボル
		Returns:
			解決可否, シンボル
		Note:
			T -> Boundary
		"""
		# XXX constraintsも対応が必要だが、constraintsは候補が複数あり、推論にコンテキストが必要になってコストが激増してしまうため、一旦boundaryのみ対応
		if isinstance(symbol.types, defs.TemplateClass) and isinstance(symbol.types.boundary, defs.Type):
			return True, symbol.to(symbol.types, self.reflections.type_of(symbol.types.boundary))
		else:
			return False, symbol

	def _actualize_alt(self, symbol: IReflection) -> tuple[bool, IReflection]:
		"""AltClass型から実体型を解決

		Args:
			symbol: シンボル
		Returns:
			解決可否, シンボル
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
			operator: 演算子ノード
			value: 値のシンボル
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
		"""
		method = self._find_method(instance, instance.types.operations.operation_by(operator.tokens))
		if method is None:
			return None

		# XXX 算術演算以外(比較/ビット演算)は返却型が左右で必ず同じであり、戻り値の型の選別が不要であるため省略する
		if not instance.types.operations.arthmetical(operator.tokens):
			return method.returns(value)

		parameter = method.parameter_at(0, value)
		parameter_types = parameter.attrs if parameter.impl(refs.Object).type_is(Union) else [parameter]
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
			symbol: シンボル
			method_name: メソッド名
		Returns:
			シンボル
		"""
		try:
			return symbol.to(symbol.types, self.reflections.resolve(symbol.types, method_name)).impl(refs.Function)
		except Errors.UnresolvedSymbol:
			return None


class PropertiesTrait(TraitImpl, IProperties):
	"""トレイト実装(プロパティー管理)"""

	@implements
	def prop_of(self, prop: defs.Var, instance: IReflection) -> IReflection:
		"""配下のプロパティーを取得

		Args:
			prop: 変数参照ノード
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
		Note:
			### テンプレート解決の条件について
			1. メソッドを除外: メソッドは別途テンプレート解決しているため不要
			2. ローカル参照以外を除外: 実行時型参照のみ解決が必要。逆に言えば宣言領域のテンプレート解決は不要
			3. テンプレート解決不要の状態を除外: プロパティーにテンプレート型がない、またはレシーバにテンプレート型が含まれる場合はテンプレート解決は不要
		"""
		symbol = self.reflections.resolve_property(instance.types, prop)
		if symbol.types.is_a(defs.Function):
			return symbol

		if not instance.decl.is_a(*defs.DeclVarsTs):
			return symbol

		if not templates.TemplateManipulator.has_templates(symbol) or templates.TemplateManipulator.has_templates(instance):
			return symbol

		decl_actual = self._declare_class(prop, instance)
		decl_schema = self.reflections.resolve(decl_actual.types)
		actual_prop = templates.Class(symbol, {'klass': decl_schema, 'prop': symbol}).prop(decl_actual)
		return symbol.to(symbol.node, actual_prop)

	def _declare_class(self, prop: defs.Var, instance: IReflection) -> IReflection:
		"""プロパティーの定義元のクラスシンボルを解決

		Args:
			prop: 変数参照ノード
			instance: 参照元のクラスシンボル
		Returns:
			定義元のクラスシンボル
		Raises:
			Errors.Never: プロパティーの解決に失敗 ※未到達の想定
		"""
		begin_types = instance.types.as_a(defs.Class)
		prop_name = prop.domain_name
		if prop_name in begin_types.decl_this_vars:
			return instance

		inherits = begin_types.inherits
		while len(inherits) > 0:
			inherit = self.reflections.type_of(inherits.pop(0))
			inherit_types = inherit.types.as_a(defs.Class)
			if prop_name in inherit_types.decl_this_vars:
				return inherit

			inherits.extend(inherit_types.inherits)

		raise Errors.Never(prop, instance, 'Property unresolved')

	@implements
	def constructor(self, instance: IReflection) -> IReflection:
		"""コンストラクターを取得

		Args:
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
		"""
		return self.reflections.resolve_constructor(instance.types.as_a(defs.Class))


class IteratorTrait(TraitImpl, IIterator):
	"""トレイト実装(イテレーター)"""

	@implements
	def iterates(self, instance: IReflection) -> IReflection:
		"""イテレーターの結果を解決

		Args:
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
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
			symbol: シンボル
		Returns:
			シンボル
		"""
		try:
			return self.reflections.resolve(symbol.types, symbol.types.operations.iterator)
		except Errors.UnresolvedSymbol:
			return self.reflections.resolve(symbol.types, symbol.types.operations.iterable)


class FunctionTrait(TraitImpl, IFunction):
	"""トレイト実装(ファンクション)"""

	@implements
	def parameter_at(self, index: int, argument: IReflection, instance: IReflection) -> IReflection:
		"""引数の実体型を解決

		Args:
			index: 引数のインデックス
			argument: 引数の実体
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
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
			*arguments: 引数リスト
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			シンボル
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
			instance: シンボル ※Traitsから暗黙的に入力される
		Returns:
			テンプレート型ノードのリスト
		Note:
			XXX クラスにも同様の属性があるため、IGenericなどに分離を検討
		"""
		return self._build_helper(instance).templates()

	def _build_helper(self, symbol: IReflection) -> templates.Function:
		"""ヘルパー(ファンクション)を生成

		Args:
			symbol: シンボル
		Returns:
			ヘルパー(ファンクション)
		"""
		return templates.HelperBuilder(symbol).schema(lambda: self._build_schema(symbol)).build(templates.Function)

	def _build_schema(self, symbol: IReflection) -> templates.InjectSchemata:
		"""ヘルパー用スキーマを生成

		Args:
			symbol: シンボル
		Returns:
			ヘルパー用スキーマ
		"""
		if symbol.types.is_a(defs.Constructor):
			return {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.context}
		elif symbol.types.is_a(defs.Method, defs.ClassMethod):
			return {'klass': symbol.attrs[0], 'parameters': symbol.attrs[1:-1], 'returns': symbol.attrs[-1]}
		else:
			return {'parameters': symbol.attrs[:-1], 'returns': symbol.attrs[-1]}
