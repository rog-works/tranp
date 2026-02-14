from collections.abc import Callable
from typing import Generic, TypeAlias, TypeVar, override

import rogw.tranp.lang.sequence as seqs
import rogw.tranp.semantics.reflection.definition as refs
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.compatible.python.types import Union
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import Errors
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.syntax.node.node import Node

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
			Errors.Never: 存在しないキーを指定
		"""
		if key in self.__schemata:
			return self.__schemata[key]

		raise Errors.Never(key, 'Schema not defined')


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
		return list({symbol: True for symbol in schema_templates.values()}.keys())


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
		return list({symbol: True for symbol in schema_templates.values() if symbol not in ignore_templates}.keys())


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
	def has_templates(cls, symbol: IReflection) -> bool:
		"""シンボル内にテンプレート型が存在するか判定

		Args:
			symbol: シンボル
		Returns:
			True = 存在
		"""
		return len(cls.unpack_templates(temp=symbol)[0]) > 0

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
		normalize_schema_props = cls._normalize_props(schema_props)
		normalize_actual_props = cls._normalize_props(actual_props)
		for target_path, target_template in target_templates.items():
			for schema_path, schema_template in schema_templates.items():
				if target_template != schema_template:
					continue

				found_path = cls._find_actual_path(schema_path, normalize_schema_props, normalize_actual_props)
				if len(found_path) == 0:
					continue

				updates[target_path] = found_path

				# 実体型を解決した時点でtarget_pathに対する解析は成功
				if not actual_props[found_path].types.is_a(defs.TemplateClass):
					break

		return updates

	@classmethod
	def _normalize_props(cls, props: dict[str, IReflection]) -> dict[str, str]:
		"""シンボルのマップ表を正規化(=単純化)

		Args:
			props: シンボルのマップ表
		Returns:
			正規化したマップ表
		Note:
			@see tests.unit.rogw.tranp.semantics.reflection.test_helper.py
		"""
		unique_keys: list[str] = []
		keys = list(props.keys())
		for i, key in enumerate(keys):
			found = False
			for j in range(i + 1, len(keys)):
				if keys[j].startswith(key):
					found = True
					break

			# 1階層目(klass/returns)は選別が不要なため除外
			if not found and DSN.elem_counts(key) > 1:
				unique_keys.append(key)

		elem_indexs: dict[str, list[int]] = {key: [] for key in unique_keys}
		for key in unique_keys:
			count = DSN.elem_counts(key)
			for i in range(2, count):
				begin = DSN.left(key, i)
				# Unionは条件を並列に並べることが目的。seq.expandによって既に展開されており、階層としては不要なので除外
				if begin in props and not props[begin].impl(refs.Object).type_is(Union):
					begin_index = int(DSN.right(begin, 1))
					elem_indexs[key].append(begin_index)

			index = int(DSN.right(key, 1))
			elem_indexs[key].append(index)

		return {key: DSN.join(*map(str, indexs)) for key, indexs in elem_indexs.items()}

	@classmethod
	def _find_actual_path(cls, schema_path: str, schema_props: dict[str, str], actual_props: dict[str, str]) -> str:
		"""テンプレート型に対応する実行時型のシンボルへのパスを探索

		Args:
			schema_path: 対象のスキーマのパス
			schema_elems: 正規化したシンボルの階層パス(スキーマ)
			actual_props: 正規化したシンボルのマップ表(実行時型)
		Returns:
			実行時型のパス
		Note:
			@see tests.unit.rogw.tranp.semantics.reflection.test_helper.py
		"""
		# 1階層目(klass/returns)は選別が不要なため、そのまま返却
		if DSN.elem_counts(schema_path) == 1:
			return schema_path

		schema_elems = schema_props[schema_path]
		schema_path_begin = DSN.left(schema_path, 2)
		for actual_path, actual_elems in actual_props.items():
			if not actual_path.startswith(schema_path_begin):
				continue
			elif actual_elems == schema_elems:
				return actual_path
			elif actual_elems.startswith(schema_elems):
				# 正規化後はスキーマより実行時型の方が必ず長い
				lacks = DSN.elem_counts(actual_elems) - DSN.elem_counts(schema_elems)
				return DSN.left(actual_path, DSN.elem_counts(actual_path) - lacks)

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
			Errors.Never: ビルド対象が期待する型と不一致
		"""
		ctors: dict[type[defs.ClassDef], type[Helper]] = {
			defs.Function: Function,
			defs.ClassMethod: ClassMethod,
			defs.Method: Method,
			defs.Constructor: Constructor,
		}
		ctor = ctors.get(self.__symbol.types.__class__, Function)
		if not issubclass(ctor, expect):
			raise Errors.Never(self.__symbol.node, self.__symbol, ctor, expect, 'Unmatch build class')

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
