from typing import Callable, Generic, TypeAlias, TypeVar

from rogw.tranp.errors import LogicError
from rogw.tranp.lang.annotation import override
import rogw.tranp.lang.sequence as seqs
from rogw.tranp.syntax.ast.dsn import DSN
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.reflection.interface import IReflection

T_Helper = TypeVar('T_Helper', bound='Helper')
T_Schemata = TypeVar('T_Schemata', IReflection, list[IReflection])

InjectSchemata: TypeAlias = dict[str, IReflection | list[IReflection]]
Injector: TypeAlias = Callable[[], InjectSchemata]


class Schema(Generic[T_Schemata]):
	"""シンボルをスキーマとして管理"""

	def __init__(self, schemata: dict[str, T_Schemata]) -> None:
		"""インスタンスを生成

		Args:
			schemata (T_Schemata): プロパティー名とシンボルのマップ情報
		"""
		self.__schemata = schemata

	def __getattr__(self, key: str) -> T_Schemata:
		"""プロパティー名に対応するシンボルを取得

		Args:
			key (str): プロパティー名
		Returns:
			T_Schemata: シンボル | シンボルリスト
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
			symbol (IReflection): シンボル
			schemata (InjectSchemata): プロパティー名とシンボルのマップ情報
		"""
		self.symbol = symbol
		self.schema = Schema[IReflection]({key: schema for key, schema in schemata.items() if isinstance(schema, IReflection)})
		self.schemata = Schema[list[IReflection]]({key: schema for key, schema in schemata.items() if type(schema) is list})

	def is_a(self, *ctors: type['Helper']) -> bool:
		"""指定のクラスと同じか派生クラスか判定

		Args:
			*ctors (type[Helper]): 比較対象
		Returns:
			bool: True = 同種
		"""
		return isinstance(self, ctors)


class Class(Helper):
	"""クラス"""

	def definition(self, *context: IReflection) -> IReflection:
		"""クラス定義の実行時型を解決

		Args:
			*context (IReflection): コンテキスト
		Returns:
			IReflection: 実行時型
		"""
		map_props = TemplateManipulator.unpack_symbols(template_types=list(context))
		t_map_props = TemplateManipulator.unpack_templates(template_types=self.schemata.template_types)
		updates = TemplateManipulator.make_updates(t_map_props, t_map_props, map_props)
		return TemplateManipulator.apply(self.schema.klass.clone(), map_props, updates)


class Function(Helper):
	"""全ファンクションの基底クラス。メソッド/クロージャー以外のファンクションが対象"""

	def parameter(self, index: int, *context: IReflection) -> IReflection:
		"""引数の実行時型を解決

		Args:
			index (int): 引数のインデックス
			*context (IReflection): コンテキスト(0: 引数(実行時型))
		Returns:
			IReflection: 実行時型
		"""
		argument, *_ = context
		return argument

	def returns(self, *arguments: IReflection) -> IReflection:
		"""戻り値の実行時型を解決

		Args:
			*arguments (IReflection): 引数リスト(実行時型)
		Returns:
			IReflection: 実行時型
		"""
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(t_map_returns) == 0:
			return self.schema.returns

		map_props = TemplateManipulator.unpack_symbols(parameters=list(arguments))
		t_map_props = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props, map_props)
		return TemplateManipulator.apply(self.schema.returns.clone(), map_props, updates)

	def templates(self) -> list[defs.TemplateClass]:
		"""テンプレート型(タイプ再定義ノード)を取得

		Returns:
			list[TemplateClass]: テンプレート型リスト
		"""
		t_map_props = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters, returns=self.schema.returns)
		return list(t_map_props.values())


class Closure(Function):
	"""クロージャー"""
	pass


class Method(Function):
	"""全メソッドの基底クラス。クラスメソッド/コンストラクター以外のメソッドが対象"""

	@override
	def parameter(self, index: int, *context: IReflection) -> IReflection:
		"""引数の実行時型を解決

		Args:
			index (int): 引数のインデックス
			*context (IReflection): コンテキスト(0: レシーバー(実行時型), 1: 引数(実行時型))
		Returns:
			IReflection: 実行時型
		"""
		parameter = self.schemata.parameters[index]
		t_map_parameter = TemplateManipulator.unpack_templates(parameter=parameter)
		if len(t_map_parameter) == 0:
			return parameter

		actual_klass, *_ = context
		map_props = TemplateManipulator.unpack_symbols(klass=actual_klass)
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass)
		updates = TemplateManipulator.make_updates(t_map_parameter, t_map_props, map_props)
		return TemplateManipulator.apply(parameter.clone(), map_props, updates)

	@override
	def returns(self, *arguments: IReflection) -> IReflection:
		"""戻り値の実行時型を解決

		Args:
			*arguments (IReflection): 引数リスト(実行時型)
		Returns:
			IReflection: 実行時型
		"""
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(t_map_returns) == 0:
			return self.schema.returns

		actual_klass, *actual_arguments = arguments
		map_props = TemplateManipulator.unpack_symbols(klass=actual_klass, parameters=actual_arguments)
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props, map_props)
		return TemplateManipulator.apply(self.schema.returns.clone(), map_props, updates)

	@override
	def templates(self) -> list[defs.TemplateClass]:
		"""テンプレート型(タイプ再定義ノード)を取得

		Returns:
			list[TemplateClass]: テンプレート型リスト
		"""
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters, returns=self.schema.returns)
		ignore_ts = [t for path, t in t_map_props.items() if path.startswith('klass')]
		return list(set([t for t in t_map_props.values() if t not in ignore_ts]))


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
	def unpack_templates(cls, **attrs: IReflection | list[IReflection]) -> TemplateMap:
		"""シンボル/属性からテンプレート型(タイプ再定義ノード)を平坦化して抽出

		Args:
			**attrs (IReflection | list[IReflection]): シンボル/属性
		Returns:
			TemplateMap: パスとテンプレート型(タイプ再定義ノード)のマップ表
		"""
		expand_attrs = seqs.expand(attrs, iter_key='attrs')
		return {path: attr.types for path, attr in expand_attrs.items() if isinstance(attr.types, defs.TemplateClass)}

	@classmethod
	def unpack_symbols(cls, **attrs: IReflection | list[IReflection]) -> SymbolMap:
		"""シンボル/属性を平坦化して抽出

		Args:
			**attrs (IReflection | list[IReflection]): シンボル/属性
		Returns:
			SymbolMap: パスとシンボルのマップ表
		"""
		return seqs.expand(attrs, iter_key='attrs')

	@classmethod
	def make_updates(cls, t_map_primary: TemplateMap, t_map_props: TemplateMap, actual_props: SymbolMap) -> UpdateMap:
		"""主体とサブを比較し、一致するテンプレートのパスを抽出

		Args:
			t_map_primary (TemplateMap): 主体
			t_map_props (TemplateMap): サブ
			actual_props (SymbolMap): シンボルのマップ表(実行時型)
		Returns:
			UpdateMap: 一致したパスのマップ表
		"""
		updates: UpdateMap = {}
		for primary_path, t_primary in t_map_primary.items():
			founds = [prop_path for prop_path, t_prop in t_map_props.items() if t_prop == t_primary]
			# XXX ジェネリッククラスのクラスメソッドやコンストラクターの場合、
			# XXX 呼び出し時に自己参照の実行時型が確定できず、テンプレートタイプが含まれてしまうので、除外する
			founds = [found_path for found_path in founds if not actual_props[found_path].types.is_a(defs.TemplateClass)]
			if founds:
				updates[primary_path] = founds[0]

		return updates

	@classmethod
	def apply(cls, primary: IReflection, actual_props: SymbolMap, updates: UpdateMap) -> IReflection:
		"""シンボルに実行時型を適用する

		Args:
			primary (IReflection): 適用するシンボル
			actual_props (SymbolMap): シンボルのマップ表(実行時型)
			updates (UpdateMap): 更新表
		Returns:
			IReflection: 適用後のシンボル
		"""
		primary_bodies = [prop_path for primary_path, prop_path in updates.items() if DSN.elem_counts(primary_path) == 1]
		if primary_bodies:
			return actual_props[primary_bodies[0]]

		for primary_path, prop_path in updates.items():
			attr_path = DSN.shift(primary_path, 1)
			seqs.update(primary.attrs, attr_path, actual_props[prop_path], iter_key='attrs')

		return primary


class HelperBuilder:
	"""ヘルパービルダー"""

	def __init__(self, symbol: IReflection) -> None:
		"""インスタンスを生成

		Args:
			symbol (IReflection): シンボル
		"""
		self.__symbol = symbol
		self.__case_of_injectors: dict[str, Injector] = {'__default__': lambda: {}}

	@property
	def __current_key(self) -> str:
		"""str: 編集中のキー"""
		return list(self.__case_of_injectors.keys())[-1]

	def case(self, expect: type[Helper]) -> 'HelperBuilder':
		"""ケースを挿入

		Args:
			expect (type[Helper]): 対象のヘルパー型
		Returns:
			HelperBuilder: 自己参照
		"""
		self.__case_of_injectors[expect.__name__] = lambda: {}
		return self

	def other_case(self) -> 'HelperBuilder':
		"""その他のケースを挿入

		Returns:
			HelperBuilder: 自己参照
		"""
		self.__case_of_injectors['__other__'] = lambda: {}
		return self

	def schema(self, injector: Injector) -> 'HelperBuilder':
		"""編集中のケースにスキーマを追加

		Args:
			injector (Injector): スキーマファクトリー
		Returns:
			HelperBuilder: 自己参照
		"""
		self.__case_of_injectors[self.__current_key] = injector
		return self

	def build(self, expect: type[T_Helper]) -> T_Helper:
		"""ヘルパーを生成

		Args:
			expect (type[T_Helper]): 期待するヘルパーの型
		Returns:
			T_Helper: 生成したインスタンス
		Raises:
			LogicError: ビルド対象が期待する型と不一致 XXX 出力する例外は要件等
		"""
		ctors: dict[type[defs.ClassDef], type[Helper]] = {
			defs.Class: Class,
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
			ctor (type[Helper]): 生成する型
		Returns:
			Injector: スキーマファクトリー
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
