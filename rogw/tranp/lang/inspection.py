from enum import Enum, EnumType
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Callable, Literal, Protocol, TypeAlias

from rogw.tranp.lang.annotation import override

FuncTypes: TypeAlias = FunctionType | MethodType | property | classmethod


class SelfAttributes(Protocol):
	"""インスタンス変数明示プロトコル"""

	@classmethod
	def __self_attributes__(cls) -> dict[str, type]:
		"""インスタンス変数のスキーマを生成

		Returns:
			dict[str, type]: スキーマ
		"""
		...



class Typehint:
	"""タイプヒント(基底クラス)"""

	@property
	def origin(self) -> type:
		"""type: メインタイプ"""
		...


class ScalarTypehint(Typehint):
	"""タイプヒント(値)

	Note:
		### 対象のクラス
		* int/str/float/bool
		* list/dict/tuple/type
		* UnionType
		* EnumType
		* None/NoneType
	"""

	def __init__(self, scalar_type: type) -> None:
		"""インスタンスを生成

		Args:
			scalar_type (type): タイプ
		"""
		self._type = scalar_type

	@property
	@override
	def origin(self) -> type:
		"""type: メインタイプ"""
		return getattr(self._type, '__origin__', self._type)

	@property
	def raw(self) -> type:
		"""type: 元のタイプ"""
		return self._type

	@property
	def is_null(self) -> bool:
		"""bool: True = None"""
		return self._type is None or self._type is NoneType

	@property
	def is_generic(self) -> bool:
		"""bool: True = ジェネリック型"""
		return hasattr(self._type, '__origin__') or self.origin in [list, dict, tuple, type]

	@property
	def is_list(self) -> bool:
		"""bool: True = リスト型"""
		return self.origin is list

	@property
	def is_union(self) -> bool:
		"""bool: True = Union型"""
		return type(self._type) is UnionType

	@property
	def is_nullable(self) -> bool:
		"""bool: True = Nullable型"""
		return self.is_union and type(None) in self.__sub_annos

	@property
	def is_enum(self) -> bool:
		"""bool: True = Enum型"""
		return type(self._type) is EnumType

	@property
	def sub_types(self) -> list[Typehint]:
		"""list[Typehint]: ジェネリック/Union型のサブタイプのリスト"""
		return [Inspector.resolve(sub_type) for sub_type in self.__sub_annos]

	@property
	def __sub_annos(self) -> list[type]:
		"""list[type]: ジェネリック/Union型のサブタイプのリスト"""
		return getattr(self._type, '__args__', [])

	@property
	def enum_members(self) -> list[Enum]:
		"""dict[str, Enum]: Enumのメンバー一覧"""
		return list(getattr(self.origin, '__members__').values())


class FunctionTypehint(Typehint):
	"""タイプヒント(関数)

	Note:
		### 対象のクラス
		* 関数
		* メソッド(クラス/インスタンス)
		### 非対応
		* ラムダ ※タイプヒントが付けられないため
	"""

	def __init__(self, func: FuncTypes | Callable) -> None:
		"""インスタンスを生成

		Args:
			func (FuncTypes | Callable): 関数オブジェクト
		Note:
			XXX コンストラクターはFuncTypeに当てはまらないため、Callableとして受け付ける
		"""
		self._func = func

	@property
	@override
	def origin(self) -> type:
		"""type: メインタイプ"""
		return type(self._func)

	@property
	def raw(self) -> FuncTypes | Callable:
		""" FuncTypes | Callable: 関数オブジェクト"""
		return self._func

	@property
	def func_type(self) -> Literal['classmethod', 'method', 'function']:
		"""関数の種別を取得

		Returns:
			Literal['classmethod', 'method', 'function']: 関数の種別
		Note:
			XXX Pythonではメソッドはオブジェクトに動的にバインドされるため、タイプから関数オブジェクトを取得した場合、メソッドとして判定する方法がない ※Pythonの仕様
		"""
		if self.origin is classmethod or isinstance(getattr(self._func, '__self__', None), type):
			return 'classmethod'
		elif self.origin in [MethodType, property]:
			return 'method'
		else:
			return 'function'

	@property
	def args(self) -> dict[str, Typehint]:
		"""dict[str, Typehint]: 引数リスト"""
		return {key: Inspector.resolve(in_type) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def returns(self) -> Typehint:
		"""Typehint: 戻り値"""
		return Inspector.resolve(self.__annos['return'])

	@property
	def __annos(self) -> dict[str, type]:
		"""dict[str, type]: タイプヒントのリスト"""
		if hasattr(self._func, '__annotations__'):
			return self._func.__annotations__
		else:
			# XXX propertyは`__annotations__`が無いため、元の関数オブジェクトを通して取得する
			return getattr(self._func, 'fget').__annotations__


class ClassTypehint(Typehint):
	"""タイプヒント(クラス)

	Note:
		### 対象のクラス
		* クラス全般
		### 注意事項
		* @see class_vars クラス変数の展開
		* @see self_vars インスタンス変数の展開
	"""

	def __init__(self, class_type: type) -> None:
		"""インスタンスを生成

		Args:
			class_type (type): クラス
		"""
		self._type = class_type

	@property
	@override
	def origin(self) -> type:
		"""type: メインタイプ"""
		return self._type

	@property
	def constructor(self) -> FunctionTypehint:
		"""FunctionTypehint: コンストラクター"""
		return FunctionTypehint(self._type.__init__)

	@property
	def class_vars(self) -> dict[str, Typehint]:
		"""クラス変数の一覧を取得

		Returns:
			dict[str, Typehint]: クラス変数一覧
		Note:
			Pythonではクラス変数とインスタンス変数の差が厳密ではないため、
			このクラスではクラス直下に定義された変数をクラス変数と位置づける
		"""
		return {key: Inspector.resolve(attr) for key, attr in self.__recursive_annos(self._type).items()}

	def __recursive_annos(self, _type: type) -> dict[str, type]:
		"""クラス階層を辿ってタイプヒントを収集

		Args:
			_type (type): タイプ
		Returns:
			dict[str, type]: タイプヒント一覧
		"""
		annos: dict[str, type] = {}
		for at_type in reversed(_type.mro()):
			annos = {**annos, **getattr(at_type, '__annotations__', {})}

		return annos

	@property
	def self_vars(self) -> dict[str, Typehint]:
		"""インスタンス変数の一覧を取得

		Returns:
			dict[str, Typehint]: インスタンス変数一覧
		Note:
			Pythonではインスタンス変数はオブジェクトに動的にバインドされるため、タイプから抜き出す方法が無い
			そのため、独自の特殊メソッド`__self_attributes__`を実装することで対処する
			@see SelfAttributes
		"""
		attrs: dict[str, type] = {}
		if hasattr(self._type, SelfAttributes.__self_attributes__.__name__):
			attrs = getattr(self._type, SelfAttributes.__self_attributes__.__name__)()

		return {key: Inspector.resolve(attr) for key, attr in attrs.items()}

	@property
	def methods(self) -> dict[str, FunctionTypehint]:
		"""dict[str, FunctionTypehint]: メソッド一覧"""
		return {key: FunctionTypehint(prop) for key, prop in self.__recursive_methods(self._type).items()}

	def __recursive_methods(self, _type: type) -> dict[str, FuncTypes]:
		"""クラス階層を辿ってメソッドを収集

		Args:
			_type (type): タイプ
		Returns:
			dict[str, FuncTypes]: メソッド一覧
		"""
		_methods: dict[str, FuncTypes] = {}
		for at_type in reversed(_type.mro()):
			for key, attr in at_type.__dict__.items():
				if isinstance(attr, FuncTypes):
					_methods[key] = attr

		return _methods


class Inspector:
	"""タイプヒントリゾルバー"""

	@classmethod
	def resolve(cls, origin: type | FuncTypes) -> Typehint:
		"""タイプヒントを解決

		Args:
			origin (type | FuncTypes): タイプ、または関数オブジェクト
		Returns:
			Typehint: タイプヒント
		"""
		if isinstance(origin, FuncTypes):
			return FunctionTypehint(origin)
		elif cls.__is_scalar(origin):
			return ScalarTypehint(origin)
		else:
			return ClassTypehint(origin)

	@classmethod
	def __is_scalar(cls, origin: type) -> bool:
		"""値型か判定

		Args:
			origin (type): タイプ
		Returns:
			bool: True = 値型
		"""
		if isinstance(origin, type) and issubclass(origin, (int, str, float, bool)):
			return True
		elif getattr(origin, '__origin__', origin) in [list, dict, tuple, type]:
			return True
		elif type(origin) in [UnionType, EnumType]:
			return True
		elif origin is None or origin is NoneType:
			return True
		else:
			return False

	@classmethod
	def validation(cls, aggregate: type['SelfAttributes'], factory: Callable[[], 'SelfAttributes'] | None = None) -> bool:
		"""SelfAttributes準拠クラスのバリデーション

		Args:
			aggregate (type[SelfAttributes]): 検証クラス
			factory (Callable[[], SelfAttributes] | None): インスタンスファクトリー (default = None)
		Returns:
			bool: True = 成功
		Raises:
			TypeError: 設計と相違したスキーマ
			TypeError: インスタンスの生成に失敗
		"""
		if not hasattr(aggregate, SelfAttributes.__self_attributes__.__name__):
			raise TypeError(f'"{SelfAttributes.__self_attributes__.__name__}" is not implemented. class: {aggregate}')

		instance: SelfAttributes | None = None
		try:
			instance = factory() if factory else aggregate()
		except Exception as e:
			raise TypeError(f'Failed create instance. validation incomplete. class: {aggregate}, error: {e}')

		hint = ClassTypehint(aggregate)
		for key, attr_hint in hint.self_vars.items():
			if not hasattr(instance, key):
				raise TypeError(f'"{key}" is not defined. class: {aggregate}')

			actual_type = type(getattr(instance, key))
			if attr_hint.origin != actual_type:
				raise TypeError(f'"{key}" is unexpected type. required "{attr_hint.origin}" from "{actual_type}". class: {aggregate}')

		return True
