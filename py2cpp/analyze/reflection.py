from typing import Generic, TypeAlias, TypeVar

from py2cpp.analyze.symbol import SymbolRaw
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import override
import py2cpp.lang.sequence as seqs
import py2cpp.node.definition as defs

T_Ref = TypeVar('T_Ref', bound='Reflection')
T_Sym = TypeVar('T_Sym', SymbolRaw, list[SymbolRaw], 'Object')

InjectSchemata: TypeAlias = dict[str, SymbolRaw | list[SymbolRaw]]


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
		self.schema = Schema[SymbolRaw]({key: schema for key, schema in schemata.items() if type(schema) is SymbolRaw})
		self.schemata = Schema[list[SymbolRaw]]({key: schema for key, schema in schemata.items() if type(schema) is list})

	@property
	def types(self) -> defs.ClassDef:
		"""ClassDef: シンボルのクラス型(クラス定義ノード)"""
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
		"""
		if isinstance(self, ctor):
			return self

		raise LogicError(f'Cast not allowed. from: {self.__class__.__name__}, to: {ctor.__name__}')


class Object(Reflection):
	"""全クラスの基底クラス"""
	...


class Instance(Object):
	"""クラスインスタンスの基底クラス"""

	@property
	def is_static(self) -> bool:
		...

	def props(self, key: str) -> Object:
		...


class Enum(Object):
	"""Enum"""
	...


class Function(Object):
	"""全ファンクションの基底クラス。素のファンクションが該当"""

	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 戻り値の実行時型
		"""
		map_props = TemplateManipulator.unpack_symbols(parameters=list(arguments))
		t_map_props = TemplateManipulator.unpack_templates(parameters=self.schemata.parameters, returns=self.schema.returns)
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
		return TemplateManipulator.apply(self.schema.returns.clone(), map_props, updates)


class Closure(Function):
	"""クロージャー"""
	...


class Method(Function):
	"""全メソッドの基底クラス"""

	@override
	def returns(self, *arguments: SymbolRaw) -> SymbolRaw:
		"""戻り値の実行時型を解決

		Args:
			*arguments (SymbolRaw): 引数リスト(実行時型)
		Returns:
			SymbolRaw: 戻り値の実行時型
		"""
		map_props = TemplateManipulator.unpack_symbols(klass=list(arguments)[0], parameters=list(arguments)[1:])
		t_map_props = TemplateManipulator.unpack_templates(klass=self.schema.klass, parameters=self.schemata.parameters)
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.schema.returns)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
		return TemplateManipulator.apply(self.schema.returns.clone(), map_props, updates)


class ClassMethod(Method):
	"""クラスメソッド"""
	...

class Constructor(Method):
	"""コンストラクター"""
	...


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
			t_map_prop (TemplateMap): サブ
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
		"""
		primary_bodies = [prop_path for primary_path, prop_path in updates.items() if DSN.elem_counts(primary_path) == 1]
		if primary_bodies:
			return actual_props[primary_bodies[0]]

		for primary_path, prop_path in updates.items():
			seqs.update(primary.attrs, primary_path, actual_props[prop_path], iter_key='attrs')

		return primary


class Builder:
	"""リフレクションビルダー"""

	def __init__(self, symbol: SymbolRaw) -> None:
		"""インスタンスを生成

		Args:
			symbol (SymbolRaw): シンボル
		"""
		self.__symbol = symbol
		self.__case_of_schemata: dict[str, InjectSchemata] = {'__default__': {}}

	@property
	def __current_key(self) -> str:
		"""str: 編集中のキー"""
		return list(self.__case_of_schemata.keys())[-1]

	def case(self, expect: type[Reflection]) -> 'Builder':
		"""ケースを挿入

		Args:
			expect (type[Reflection]): 対象のリフレクション型
		Returns:
			Builder: 自己参照
		"""
		self.__case_of_schemata[expect.__name__] = {}
		return self

	def other_case(self) -> 'Builder':
		"""その他のケースを挿入

		Returns:
			Builder: 自己参照
		"""
		self.__case_of_schemata['__other__'] = {}
		return self

	def schema(self, **schemata: SymbolRaw | list[SymbolRaw]) -> 'Builder':
		"""編集中のケースにスキーマを追加

		Args:
			**schemata (SymbolRaw | list[SymbolRaw]): スキーマとなるシンボル
		Returns:
			Builder: 自己参照
		"""
		self.__case_of_schemata[self.__current_key] = {**self.__case_of_schemata[self.__current_key], **schemata}
		return self

	def build(self, expect: type[T_Ref]) -> T_Ref:
		"""リフレクションを生成

		Args:
			target (type[T_Ref]): レスポンスするリフレクション型
		"""
		ctors: dict[type[defs.ClassDef], type[Reflection]] = {
			defs.Function: Function,
			defs.ClassMethod: ClassMethod,
			defs.Method: Method,
			defs.Constructor: Constructor,
		}
		ctor = ctors[self.__symbol.types.__class__]
		if not issubclass(ctor, expect):
			raise LogicError(f'Reflection build not supported. expect: {expect}')

		return ctor(self.__symbol, self.__inject_schemata(ctor))

	def __inject_schemata(self, ctor: type[Reflection]) -> InjectSchemata:
		"""生成時に注入するスキーマを取得

		Args:
			ctor (type[Reflection]): 生成するリフレクション型
		Returns:
			InjectSchemata: スキーマ
		"""
		for ctor_ in ctor.__mro__:
			if not issubclass(ctor_, Reflection):
				break

			if ctor_.__name__ in self.__case_of_schemata:
				return self.__case_of_schemata[ctor_.__name__]

		if '__other__' in self.__case_of_schemata:
			return self.__case_of_schemata['__other__']
		else:
			return self.__case_of_schemata['__default__']

