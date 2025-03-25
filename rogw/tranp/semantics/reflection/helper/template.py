from collections.abc import Callable
from typing import Generic, TypeAlias, TypeVar, override

from rogw.tranp.compatible.python.types import Union
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import LogicError
import rogw.tranp.lang.sequence as seqs
from rogw.tranp.semantics.reflection.base import IReflection
import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.syntax.node.definition as defs

T_Helper = TypeVar('T_Helper', bound='Helper')
T_Schemata = TypeVar('T_Schemata', IReflection, list[IReflection])

InjectSchemata: TypeAlias = dict[str, IReflection | list[IReflection]]
Injector: TypeAlias = Callable[[], InjectSchemata]


class Schema(Generic[T_Schemata]):
	"""シンボルをスキーマとして管理"""

	def __init__(self, schemata: dict[str, T_Schemata]) -> None:
		"""インスタンスを生成

		Args:
			schemata: プロパティー名とシンボルのマップ情報
		"""
		self.__schemata = schemata

	def __getattr__(self, key: str) -> T_Schemata:
		"""プロパティー名に対応するシンボルを取得

		Args:
			key: プロパティー名
		Returns:
			シンボル | シンボルリスト
		Raises:
			LogicError: 存在しないキーを指定 XXX 出力する例外は要件等
		"""
		if key in self.__schemata:
			return self.__schemata[key]

		raise LogicError(f'Schema not defined. key: {key}')


class Helper:
	"""テンプレート解決ヘルパー"""

	def __init__(self, symbol: IReflection, schemata: InjectSchemata) -> None:
		"""インスタンスを生成

		Args:
			symbol: シンボル
			schemata: プロパティー名とシンボルのマップ情報
		"""
		self.symbol = symbol
		self.schema = Schema[IReflection]({key: schema for key, schema in schemata.items() if isinstance(schema, IReflection)})
		self.schemata = Schema[list[IReflection]]({key: schema for key, schema in schemata.items() if type(schema) is list})

	def is_a(self, *ctors: type['Helper']) -> bool:
		"""指定のクラスと同じか派生クラスか判定

		Args:
			*ctors: 比較対象
		Returns:
			True = 同種
		"""
		return isinstance(self, ctors)


class Class(Helper):
	"""クラス"""

	def prop(self, actual_klass: IReflection) -> IReflection:
		"""戻り値の実行時型を解決

		Args:
			actual_klass: クラス(実行時型)
		Returns:
			実行時型
		"""
		prop_templates, _ = TemplateManipulator.unpack_templates(prop=self.schema.prop)
		if len(prop_templates) == 0:
			return self.schema.prop

		actual_props = TemplateManipulator.unpack_symbols(klass=actual_klass)
		schema_templates, schema_props = TemplateManipulator.unpack_templates(klass=self.schema.klass)
		updates = TemplateManipulator.make_updates(prop_templates, schema_templates, schema_props, actual_props)
		return TemplateManipulator.apply(self.schema.prop.to_temporary(), actual_props, updates)


class Function(Helper):
	"""全ファンクションの基底クラス。メソッド/クロージャー以外のファンクションが対象"""

	def parameter(self, index: int, *context: IReflection) -> IReflection:
		"""引数の実行時型を解決

		Args:
			index: 引数のインデックス
			*context: コンテキスト(0: 引数(実行時型))
		Returns:
			実行時型
		"""
		argument, *_ = context
		return argument

	def returns(self, *arguments: IReflection) -> IReflection:
		"""戻り値の実行時型を解決

		Args:
			*arguments: 引数リスト(実行時型)
		Returns:
			実行時型
		"""
		return_templates, _ = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(return_templates) == 0:
			return self.schema.returns

		actual_props = TemplateManipulator.unpack_symbols(parameters=list(arguments))
		param_templates, schema_props = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(return_templates, param_templates, schema_props, actual_props)
		return TemplateManipulator.apply(self.schema.returns.to_temporary(), actual_props, updates)

	def templates(self) -> list[defs.TemplateClass]:
		"""テンプレート型を取得

		Returns:
			テンプレート型リスト
		"""
		schema_templates, _ = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters, returns=self.schema.returns)
		return list(set(schema_templates.values()))


class Closure(Function):
	"""クロージャー"""
	pass


class Method(Function):
	"""全メソッドの基底クラス。クラスメソッド/コンストラクター以外のメソッドが対象"""

	@override
	def parameter(self, index: int, *context: IReflection) -> IReflection:
		"""引数の実行時型を解決

		Args:
			index: 引数のインデックス
			*context: コンテキスト(0: レシーバー(実行時型), 1: 引数(実行時型))
		Returns:
			実行時型
		Note:
			FIXME Union型の引数にテンプレート型が含まれると解決に失敗する
		"""
		parameter = self.schemata.parameters[index]
		param_templates, _ = TemplateManipulator.unpack_templates(parameter=parameter)
		if len(param_templates) == 0:
			return parameter

		actual_klass, actual_parameter = context
		actual_props = TemplateManipulator.unpack_symbols(klass=actual_klass, parameter=actual_parameter)
		schema_templates, schema_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameter=parameter)
		updates = TemplateManipulator.make_updates(param_templates, schema_templates, schema_props, actual_props)
		return TemplateManipulator.apply(parameter.to_temporary(), actual_props, updates)

	@override
	def returns(self, *arguments: IReflection) -> IReflection:
		"""戻り値の実行時型を解決

		Args:
			*arguments: 引数リスト(実行時型)
		Returns:
			実行時型
		Note:
			FIXME Union型の引数にテンプレート型が含まれると解決に失敗する
		"""
		return_templates, _ = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(return_templates) == 0:
			return self.schema.returns

		actual_klass, *actual_arguments = arguments
		actual_props = TemplateManipulator.unpack_symbols(klass=actual_klass, parameters=actual_arguments)
		schema_templates, schema_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(return_templates, schema_templates, schema_props, actual_props)
		return TemplateManipulator.apply(self.schema.returns.to_temporary(), actual_props, updates)

	@override
	def templates(self) -> list[defs.TemplateClass]:
		"""テンプレート型を取得

		Returns:
			テンプレート型リスト
		"""
		schema_templates, _ = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters, returns=self.schema.returns)
		ignore_templates = [symbol for path, symbol in schema_templates.items() if path.startswith('klass')]
		return list(set([symbol for symbol in schema_templates.values() if symbol not in ignore_templates]))


class ClassMethod(Method):
	"""クラスメソッド"""
	pass


class Constructor(Method):
	"""コンストラクター"""
	pass


TemplateMap: TypeAlias = dict[str, defs.TemplateClass]
SymbolMap: TypeAlias = dict[str, IReflection]
UpdateMap: TypeAlias = dict[str, str]


class TemplateManipulator:
	"""テンプレート操作"""

	@classmethod
	def unpack_templates(cls, **attrs: IReflection | list[IReflection]) -> tuple[TemplateMap, SymbolMap]:
		"""シンボル/属性からテンプレート型を平坦化して抽出

		Args:
			**attrs: シンボル/属性
		Returns:
			(パスとテンプレート型のマップ表, パスとシンボルのマップ表)
		"""
		symbols = cls.unpack_symbols(**attrs)
		templates = {path: attr.types for path, attr in symbols.items() if isinstance(attr.types, defs.TemplateClass)}
		return templates, symbols

	@classmethod
	def unpack_symbols(cls, **attrs: IReflection | list[IReflection]) -> SymbolMap:
		"""シンボル/属性を平坦化して抽出

		Args:
			**attrs: シンボル/属性
		Returns:
			パスとシンボルのマップ表
		"""
		return seqs.expand(attrs, iter_key='attrs')

	@classmethod
	def make_updates(cls, target_templates: TemplateMap, schema_templates: TemplateMap, schema_props: SymbolMap, actual_props: SymbolMap) -> UpdateMap:
		"""スキーマと実行時型を突き合わせて解決対象のテンプレートのパスを抽出

		Args:
			target_templates: テンプレートのマップ表(解決対象)
			schema_templates: テンプレートのマップ表(スキーマ)
			schema_props: シンボルのマップ表(スキーマ)
			actual_props: シンボルのマップ表(実行時型)
		Returns:
			一致したパスのマップ表
		"""
		updates: UpdateMap = {}
		for target_path, target_template in target_templates.items():
			for schema_path, schema_template in schema_templates.items():
				if target_template != schema_template:
					continue

				found_path = cls._find_update_path(schema_path, schema_props, actual_props)
				if len(found_path) > 0:
					updates[target_path] = found_path

		return updates

	@classmethod
	def _find_update_path(cls, schema_path: str, schema_props: SymbolMap, actual_props: SymbolMap) -> str:
		"""スキーマと実行時型を突き合わせて解決対象のテンプレートのパスを抽出

		Args:
			schema_path: スキーマのパス
			schema_props: シンボルのマップ表(スキーマ)
			actual_props: シンボルのマップ表(実行時型)
		Returns:
			一致したパス
		"""
		schema_elems = DSN.elements(schema_path)
		actual_path = ''
		schema_path = ''
		actual_index = 0
		schema_index = 0
		while schema_index < len(schema_elems):
			actual_path = DSN.join(actual_path, schema_elems[actual_index])
			schema_path = DSN.join(schema_path, schema_elems[schema_index])
			actual_index += 1
			schema_index += 1
			# スキップ(データなし)
			if actual_path not in actual_props:
				...
			# 検出なし(実体のテンプレート型が未解決)
			elif actual_props[actual_path].types.is_a(defs.TemplateClass):
				break
			# 検出成功
			elif schema_props[schema_path].types.is_a(defs.TemplateClass):
				return schema_path
			# 検証(Unionのサブクラスにテンプレート型が含まれるか)
			# XXX Unionを1階層解除すると実行時型と同じ階層を参照すると言う前提。しかし、多重でUnionが重なると誤判定になるのでは？
			elif schema_props[schema_path].impl(refs.Object).type_is(Union):
				for attr in schema_props[schema_path].attrs:
					if attr.types.is_a(defs.TemplateClass):
						return schema_path

				# 実行時型がUnion以外の場合は階層を1つスキップ
				if not actual_props[actual_path].impl(refs.Object).type_is(Union):
					schema_index += 1
			# スキップ(実体とスキーマが同一、または継承関係)
			else:
				...

		return ''

	@classmethod
	def apply(cls, primary: IReflection, actual_props: SymbolMap, updates: UpdateMap) -> IReflection:
		"""シンボルに実行時型を適用する

		Args:
			primary: 適用するシンボル
			actual_props: シンボルのマップ表(実行時型)
			updates: 更新表
		Returns:
			適用後のシンボル
		"""
		primary_bodies = [prop_path for primary_path, prop_path in updates.items() if DSN.elem_counts(primary_path) == 1]
		if primary_bodies:
			return actual_props[primary_bodies[0]]

		attrs = primary.attrs
		for primary_path, prop_path in updates.items():
			attr_path = DSN.shift(primary_path, 1)
			seqs.update(attrs, attr_path, actual_props[prop_path], iter_key='attrs')

		return primary


class HelperBuilder:
	"""ヘルパービルダー"""

	def __init__(self, symbol: IReflection) -> None:
		"""インスタンスを生成

		Args:
			symbol: シンボル
		"""
		self.__symbol = symbol
		self.__case_of_injectors: dict[str, Injector] = {'__default__': lambda: {}}

	@property
	def __current_key(self) -> str:
		"""Returns: 編集中のキー"""
		return list(self.__case_of_injectors.keys())[-1]

	def case(self, expect: type[Helper]) -> 'HelperBuilder':
		"""ケースを挿入

		Args:
			expect: 対象のヘルパー型
		Returns:
			自己参照
		"""
		self.__case_of_injectors[expect.__name__] = lambda: {}
		return self

	def other_case(self) -> 'HelperBuilder':
		"""その他のケースを挿入

		Returns:
			自己参照
		"""
		self.__case_of_injectors['__other__'] = lambda: {}
		return self

	def schema(self, injector: Injector) -> 'HelperBuilder':
		"""編集中のケースにスキーマを追加

		Args:
			injector: スキーマファクトリー
		Returns:
			自己参照
		"""
		self.__case_of_injectors[self.__current_key] = injector
		return self

	def build(self, expect: type[T_Helper]) -> T_Helper:
		"""ヘルパーを生成

		Args:
			expect: 期待するヘルパーの型
		Returns:
			生成したインスタンス
		Raises:
			LogicError: ビルド対象が期待する型と不一致 XXX 出力する例外は要件等
		"""
		ctors: dict[type[defs.ClassDef], type[Helper]] = {
			defs.Function: Function,
			defs.ClassMethod: ClassMethod,
			defs.Method: Method,
			defs.Constructor: Constructor,
		}
		ctor = ctors.get(self.__symbol.types.__class__, Function)
		if not issubclass(ctor, expect):
			raise LogicError(f'Unexpected build class. symbol: {self.__symbol}, resolved: {ctor}, expect: {expect}')

		injector = self.__resolve_injector(ctor)
		return ctor(self.__symbol, injector())

	def __resolve_injector(self, ctor: type[Helper]) -> Injector:
		"""生成時に注入するスキーマを取得

		Args:
			ctor: 生成する型
		Returns:
			スキーマファクトリー
		"""
		for ctor_ in ctor.__mro__:
			if not issubclass(ctor_, Helper):
				break

			if ctor_.__name__ in self.__case_of_injectors:
				return self.__case_of_injectors[ctor_.__name__]

		if '__other__' in self.__case_of_injectors:
			return self.__case_of_injectors['__other__']
		else:
			return self.__case_of_injectors['__default__']
