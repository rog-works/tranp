from typing import Callable, Generic, TypeAlias, TypeVar

from rogw.tranp.analyze.symbol import SymbolRaw
from rogw.tranp.ast.dsn import DSN
from rogw.tranp.errors import LogicError
from rogw.tranp.lang.implementation import override
import rogw.tranp.lang.sequence as seqs
import rogw.tranp.node.definition as defs

T_Ref = TypeVar('T_Ref', bound='Reflection')
T_Sym = TypeVar('T_Sym', SymbolRaw, list[SymbolRaw], 'Object')

InjectSchemata: TypeAlias = dict[str, SymbolRaw | list[SymbolRaw]]
Injector: TypeAlias = Callable[[], InjectSchemata]


class Schema(Generic[T_Sym]):
	"""シンボルをスキーマとして管理"""

	def __init__(self, schemata: dict[str, T_Sym]) -> None:
		"""インスタンスを生成

		Args:
			schemata (dict[str, T_Sym]): プロパティー名とシンボルのマップ情報
		"""
		self.__schemata = schemata

	def __getattr__(self, key: str) -> T_Sym:
		"""プロパティー名に対応するシンボルを取得

		Args:
			key (str): プロパティー名
		Returns:
			T_Sym: シンボル | シンボルリスト
		Raises:
			LogicError: 存在しないキーを指定 XXX 出力する例外は要件等
		"""
		if key in self.__schemata:
			return self.__schemata[key]

		raise LogicError(f'Schema not defined. key: {key}')


class Reflection:
	"""リフレクション"""

	def __init__(self, symbol: SymbolRaw, schemata: InjectSchemata) -> None:
		"""インスタンスを生成

		Args:
			symbol (SymbolRaw): シンボル
			schemata (InjectSchemata): プロパティー名とシンボルのマップ情報
		"""
		self.symbol = symbol
		self.schema = Schema[SymbolRaw]({key: schema for key, schema in schemata.items() if isinstance(schema, SymbolRaw)})
		self.schemata = Schema[list[SymbolRaw]]({key: schema for key, schema in schemata.items() if type(schema) is list})

	@property
	def types(self) -> defs.ClassDef:
		"""ClassDef: シンボルの型(クラス定義ノード)"""
		return self.symbol.types

	@property
	def shorthand(self) -> str:
		"""str: シンボルの短縮表記"""
		return str(self.symbol)

	def is_a(self, *ctors: type['Reflection']) -> bool:
		"""指定のクラスと同じか派生クラスか判定

		Args:
			*ctors (type[Reflection]): 比較対象
		Returns:
			bool: True = 同種
		"""
		return isinstance(self, ctors)

	def as_a(self, ctor: type[T_Ref]) -> T_Ref:
		"""指定のクラスと同じか派生クラスであればキャスト。一致しない場合はエラーを出力

		Args:
			ctor (type[T_Ref]): 比較対象
		Returns:
			T_Ref: キャスト後のインスタンス
		Raises:
			LogicError: 派生関係が無いクラスを指定
		"""
		if isinstance(self, ctor):
			return self

		raise LogicError(f'Cast not allowed. from: {self.__class__}, to: {ctor}')


class Object(Reflection):
	"""全クラスの基底クラス"""
	...


class Type(Object):
	"""全タイプ(クラス定義)の基底クラス"""
	...


class Enum(Object):
	"""Enum"""
	...


class Instance(Object):
	"""クラスインスタンスの基底クラス"""

	@property
	def is_static(self) -> bool:
		...


class Function(Object):
	"""全ファンクションの基底クラス。メソッド/クロージャー以外のファンクションが対象"""

	def parameter(self, index: int, *context: SymbolRaw) -> SymbolRaw:
		"""引数の実行時型を解決

		Args:
			index (int): 引数のインデックス
			*context (SymbolRaw): コンテキスト(0: 引数(実行時型))
		Returns:
			SymbolRaw: 実行時型
		"""
		argument, *_ = context
		return argument

	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		"""
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(t_map_returns) == 0:
			return self.schema.returns

		map_props = TemplateManipulator.unpack_symbols(parameters=list(arguments))
		t_map_props = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
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
	...


class Method(Function):
	"""全メソッドの基底クラス。クラスメソッド/コンストラクター以外のメソッドが対象"""

	@override
	def parameter(self, index: int, *context: SymbolRaw) -> SymbolRaw:
		"""引数の実行時型を解決

		Args:
			index (int): 引数のインデックス
			*context (SymbolRaw): コンテキスト(0: レシーバー(実行時型), 1: 引数(実行時型))
		Returns:
			SymbolRaw: 実行時型
		"""
		parameter = self.schemata.parameters[index]
		t_map_parameter = TemplateManipulator.unpack_templates(parameter=parameter)
		if len(t_map_parameter) == 0:
			return parameter

		actual_klass, *_ = context
		map_props = TemplateManipulator.unpack_symbols(klass=actual_klass)
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass)
		updates = TemplateManipulator.make_updates(t_map_parameter, t_map_props)
		return TemplateManipulator.apply(parameter.clone(), map_props, updates)

	@override
	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		"""
		return self._method_returns(*arguments)

	def _function_returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決(Function/Closure/ClassMethod/Constructor用)

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		"""
		return super().returns(*arguments)

	def _method_returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決(Method専用)

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		"""
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		if len(t_map_returns) == 0:
			return self.schema.returns

		actual_klass, *actual_arguments = arguments
		map_props = TemplateManipulator.unpack_symbols(klass=actual_klass, parameters=actual_arguments)
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
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
	@override
	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		Note:
			FIXME 継承元のMethodと一貫性がないため修正を検討
		"""
		# FIXME クラスがジェネリック型の場合、クラスのTは呼び出し時に未知である場合がほとんどであり、
		# FIXME 引数のTによる実体型の補完を妨害してしまうため、ファンクションのスキームで呼び出すことで一旦解決する
		return self._function_returns(*arguments)


class Constructor(Method):
	"""コンストラクター"""

	@override
	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 実行時型
		Note:
			FIXME 継承元のMethodと一貫性がないため修正を検討
		"""
		# FIXME クラスがジェネリック型の場合、クラスのTは呼び出し時に未知である場合がほとんどであり、
		# FIXME 引数のTによる実体型の補完を妨害してしまうため、ファンクションのスキームで呼び出すことで一旦解決する
		return self._function_returns(*arguments)


TemplateMap: TypeAlias = dict[str, defs.TemplateClass]
SymbolMap: TypeAlias = dict[str, SymbolRaw]
UpdateMap: TypeAlias = dict[str, str]


class TemplateManipulator:
	"""テンプレート操作"""

	@classmethod
	def unpack_templates(cls, **attrs: SymbolRaw | list[SymbolRaw]) -> TemplateMap:
		"""シンボル/属性からテンプレート型(タイプ再定義ノード)を平坦化して抽出

		Args:
			**attrs (SymbolRaw | list[SymbolRaw]): シンボル/属性
		Returns:
			TemplateMap: パスとテンプレート型(タイプ再定義ノード)のマップ表
		"""
		expand_attrs = seqs.expand(attrs, iter_key='attrs')
		return {path: attr.types for path, attr in expand_attrs.items() if isinstance(attr.types, defs.TemplateClass)}

	@classmethod
	def unpack_symbols(cls, **attrs: SymbolRaw | list[SymbolRaw]) -> SymbolMap:
		"""シンボル/属性を平坦化して抽出

		Args:
			**attrs (SymbolRaw | list[SymbolRaw]): シンボル/属性
		Returns:
			SymbolMap: パスとシンボルのマップ表
		"""
		return seqs.expand(attrs, iter_key='attrs')

	@classmethod
	def make_updates(cls, t_map_primary: TemplateMap, t_map_props: TemplateMap) -> UpdateMap:
		"""主体とサブを比較し、一致するテンプレートのパスを抽出

		Args:
			t_map_primary (TemplateMap): 主体
			t_map_props (TemplateMap): サブ
		Returns:
			UpdateMap: 一致したパスのマップ表
		"""
		updates: UpdateMap = {}
		for primary_path, t_primary in t_map_primary.items():
			founds = [prop_path for prop_path, t_prop in t_map_props.items() if t_prop == t_primary]
			if founds:
				updates[primary_path] = founds[0]

		return updates

	@classmethod
	def apply(cls, primary: SymbolRaw, actual_props: SymbolMap, updates: UpdateMap) -> SymbolRaw:
		"""シンボルに実行時型を適用する

		Args:
			primary (SymbolRaw): 適用するシンボル
			actual_props (SymbolMap): シンボルのマップ表(実行時型)
			updates (UpdateMap): 更新表
		Returns:
			SymbolRaw: 適用後のシンボル
		"""
		primary_bodies = [prop_path for primary_path, prop_path in updates.items() if DSN.elem_counts(primary_path) == 1]
		if primary_bodies:
			return actual_props[primary_bodies[0]]

		for primary_path, prop_path in updates.items():
			attr_path = DSN.shift(primary_path, 1)
			seqs.update(primary.attrs, attr_path, actual_props[prop_path], iter_key='attrs')

		return primary


class Builder:
	"""リフレクションビルダー"""

	def __init__(self, symbol: SymbolRaw) -> None:
		"""インスタンスを生成

		Args:
			symbol (SymbolRaw): シンボル
		"""
		self.__symbol = symbol
		self.__case_of_injectors: dict[str, Injector] = {'__default__': lambda: {}}

	@property
	def __current_key(self) -> str:
		"""str: 編集中のキー"""
		return list(self.__case_of_injectors.keys())[-1]

	def case(self, expect: type[Reflection]) -> 'Builder':
		"""ケースを挿入

		Args:
			expect (type[Reflection]): 対象のリフレクション型
		Returns:
			Builder: 自己参照
		"""
		self.__case_of_injectors[expect.__name__] = lambda: {}
		return self

	def other_case(self) -> 'Builder':
		"""その他のケースを挿入

		Returns:
			Builder: 自己参照
		"""
		self.__case_of_injectors['__other__'] = lambda: {}
		return self

	def schema(self, injector: Injector) -> 'Builder':
		"""編集中のケースにスキーマを追加

		Args:
			injector (Injector): スキーマファクトリー
		Returns:
			Builder: 自己参照
		"""
		self.__case_of_injectors[self.__current_key] = injector
		return self

	def build(self, expect: type[T_Ref]) -> T_Ref:
		"""リフレクションを生成

		Args:
			expect (type[T_Ref]): 期待するレスポンス型
		Returns:
			T_Ref: 生成したインスタンス
		Raises:
			LogicError: ビルド対象が期待する型と不一致 XXX 出力する例外は要件等
		"""
		ctors: dict[type[defs.ClassDef], type[Reflection]] = {
			defs.Function: Function,
			defs.ClassMethod: ClassMethod,
			defs.Method: Method,
			defs.Constructor: Constructor,
			defs.Enum: Enum,
			defs.Class: Type,
		}
		ctor = ctors.get(self.__symbol.types.__class__, Object)
		if not issubclass(ctor, expect):
			raise LogicError(f'Unexpected build class. symbol: {self.__symbol}, resolved: {ctor}, expect: {expect}')

		injector = self.__resolve_injector(ctor)
		return ctor(self.__symbol, injector())

	def __resolve_injector(self, ctor: type[Reflection]) -> Injector:
		"""生成時に注入するスキーマを取得

		Args:
			ctor (type[Reflection]): 生成する型
		Returns:
			Injector: スキーマファクトリー
		"""
		for ctor_ in ctor.__mro__:
			if not issubclass(ctor_, Reflection):
				break

			if ctor_.__name__ in self.__case_of_injectors:
				return self.__case_of_injectors[ctor_.__name__]

		if '__other__' in self.__case_of_injectors:
			return self.__case_of_injectors['__other__']
		else:
			return self.__case_of_injectors['__default__']
