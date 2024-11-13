from collections.abc import Callable
from enum import Enum, EnumType
from importlib import import_module
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Any, ClassVar, TypeAlias, TypeVar, Union, override

FuncTypes: TypeAlias = FunctionType | MethodType | property | classmethod


class FuncClasses(Enum):
	"""関数の種別"""
	ClassMethod = 'ClassMethod'
	Method = 'Method'
	Function = 'function'


class Typehint:
	"""タイプヒント(基底クラス)"""

	@property
	def origin(self) -> type[Any]:
		"""type[Any]: メインタイプ"""
		...

	@property
	def raw(self) -> type[Any] | FuncTypes | Callable:
		"""type[Any] | FuncTypes | Callable: 元のタイプ"""
		...


class ScalarTypehint(Typehint):
	"""タイプヒント(値)

	Note:
		### 対象のクラス
		* int/str/float/bool
		* list/dict/tuple/type
		* Union/UnionType
		* EnumType
		* None/NoneType
	"""

	_type: type[Any]

	def __init__(self, scalar_type: type[Any]) -> None:
		"""インスタンスを生成

		Args:
			scalar_type (type[Any]): タイプ
		"""
		self._type: type[Any] = scalar_type

	@property
	@override
	def origin(self) -> type[Any]:
		"""type[Any]: メインタイプ"""
		if self.is_union:
			# XXX Union型の場合はUnionTypeを返却。UnionTypeはtypeと互換性が無いと判断されるため実装例に倣う @see types.py UnionType
			return type(int | str)
		else:
			return getattr(self._type, '__origin__', self._type)

	@property
	@override
	def raw(self) -> type[Any]:
		"""type[Any]: 元のタイプ"""
		return self._type

	@property
	def is_null(self) -> bool:
		"""bool: True = None"""
		return self._type is None or self._type is NoneType

	@property
	def is_generic(self) -> bool:
		"""bool: True = ジェネリック型"""
		return getattr(self._type, '__origin__', self._type) in [list, dict, tuple, type]

	@property
	def is_union(self) -> bool:
		"""bool: True = Union型"""
		return type(self._type) is UnionType or getattr(self._type, '__origin__', self._type) is Union

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
	def __sub_annos(self) -> list[type[Any]]:
		"""list[type[Any]]: ジェネリック/Union型のサブタイプのリスト"""
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

	_func: FuncTypes | Callable

	def __init__(self, func: FuncTypes | Callable) -> None:
		"""インスタンスを生成

		Args:
			func (FuncTypes | Callable): 関数オブジェクト
		Note:
			XXX コンストラクターはFuncTypeに当てはまらないため、Callableとして受け付ける
		"""
		self._func: FuncTypes | Callable = func

	@property
	@override
	def origin(self) -> type[Any]:
		"""type[Any]: メインタイプ"""
		return type(self._func)

	@property
	@override
	def raw(self) -> FuncTypes | Callable:
		""" FuncTypes | Callable: 関数オブジェクト"""
		return self._func

	@property
	def func_class(self) -> FuncClasses:
		"""関数の種別を取得

		Returns:
			FuncClasses: 関数の種別
		Note:
			XXX Pythonではメソッドはオブジェクトに動的にバインドされるため、タイプから関数オブジェクトを取得した場合、メソッドとして判定する方法がない ※Pythonの仕様
		"""
		if self.origin is classmethod or isinstance(getattr(self._func, '__self__', None), type):
			return FuncClasses.ClassMethod
		elif self.origin in [MethodType, property]:
			return FuncClasses.Method
		else:
			return FuncClasses.Function

	@property
	def args(self) -> dict[str, Typehint]:
		"""dict[str, Typehint]: 引数リスト"""
		return {key: Inspector.resolve(in_type, self.__via_module_path) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def returns(self) -> Typehint:
		"""Typehint: 戻り値"""
		return Inspector.resolve(self.__annos['return'], self.__via_module_path)

	@property
	def __via_module_path(self) -> str:
		"""str: 関数由来のモジュールパス"""
		if isinstance(self._func, property):
			# propertyは`__module__`が無いため、元の関数オブジェクトを通して取得する
			return getattr(self._func, 'fget').__module__
		else:
			return self._func.__module__

	@property
	def __annos(self) -> dict[str, type[Any]]:
		"""dict[str, type[Any]]: タイプヒントのリスト"""
		if isinstance(self._func, property):
			# propertyは`__annotations__`が無いため、元の関数オブジェクトを通して取得する
			return getattr(self._func, 'fget').__annotations__
		else:
			return self._func.__annotations__


class ClassTypehint(Typehint):
	"""タイプヒント(クラス)

	Note:
		### 対象のクラス
		* クラス全般
		### 留意事項
		* クラス・インスタンス変数どちらもクラスの`__annotations__`から抽出
		* クラス変数: ClassVarで明示
		* インスタンス変数: ClassVar以外
	"""

	_type: type[Any]

	def __init__(self, class_type: type[Any]) -> None:
		"""インスタンスを生成

		Args:
			class_type (type[Any]): クラス
		"""
		self._type: type[Any] = class_type

	@property
	@override
	def origin(self) -> type[Any]:
		"""type[Any]: メインタイプ"""
		return getattr(self._type, '__origin__', self._type)

	@property
	@override
	def raw(self) -> type[Any]:
		"""type[Any]: 元のタイプ"""
		return self._type

	@property
	def is_generic(self) -> bool:
		"""bool: True = ジェネリック型"""
		return hasattr(self._type, '__origin__')

	@property
	def sub_types(self) -> list[Typehint]:
		"""list[Typehint]: ジェネリック型のサブタイプのリスト"""
		sub_annos: list[type[Any]] = getattr(self._type, '__args__', [])
		return [Inspector.resolve(sub_type, self._type.__module__) for sub_type in sub_annos]

	@property
	def constructor(self) -> FunctionTypehint:
		"""FunctionTypehint: コンストラクター"""
		return FunctionTypehint(self._type.__init__)

	def class_vars(self, lookup_private: bool = True) -> dict[str, Typehint]:
		"""クラス変数の一覧を取得

		Args:
			lookup_private (bool): プライベートプロパティー抽出フラグ (default = True)
		Returns:
			dict[str, Typehint]: クラス変数一覧
		"""
		annos = {key: anno for key, anno in self.__recursive_annos(self._type, lookup_private).items() if self.__try_get_origin(anno) is ClassVar}
		return {key: ClassTypehint(attr).sub_types[0] for key, attr in annos.items()}

	def self_vars(self, lookup_private: bool = True) -> dict[str, Typehint]:
		"""インスタンス変数の一覧を取得

		Args:
			lookup_private (bool): プライベートプロパティー抽出フラグ (default = True)
		Returns:
			dict[str, Typehint]: インスタンス変数一覧
		"""
		annos = {key: anno for key, anno in self.__recursive_annos(self._type, lookup_private).items() if self.__try_get_origin(anno) is not ClassVar}
		return {key: Inspector.resolve(attr, self._type.__module__) for key, attr in annos.items()}
	
	def __try_get_origin(self, anno: type[Any]) -> type[Any]:
		"""アノテーションから元のタイプ取得を試行

		Args:
			anno (type[Any]): アノテーション
		Returns:
			type[Any]: 元のタイプ
		"""
		return getattr(anno, '__origin__', anno)

	def __recursive_annos(self, _type: type[Any], lookup_private: bool) -> dict[str, type[Any]]:
		"""クラス階層を辿ってタイプヒントを収集

		Args:
			_type (type[Any]): タイプ
			lookup_private (bool): プライベート変数抽出フラグ (default = False)
		Returns:
			dict[str, type[Any]]: タイプヒント一覧
		"""
		annos: dict[str, type[Any]] = {}
		for at_type in reversed(_type.mro()):
			_annos: dict[str, type[Any]] = getattr(at_type, '__annotations__', {})
			for key, anno in _annos.items():
				if not lookup_private and key.startswith(f'_{at_type.__name__}__'):
					continue

				annos[key] = _resolve_type_from_str(anno, at_type.__module__) if isinstance(anno, str) else anno

		return annos

	@property
	def methods(self) -> dict[str, FunctionTypehint]:
		"""dict[str, FunctionTypehint]: メソッド一覧"""
		return {key: FunctionTypehint(prop) for key, prop in self.__recursive_methods(self._type).items()}

	def __recursive_methods(self, _type: type[Any]) -> dict[str, FuncTypes]:
		"""クラス階層を辿ってメソッドを収集

		Args:
			_type (type[Any]): タイプ
		Returns:
			dict[str, FuncTypes]: メソッド一覧
		"""
		_methods: dict[str, FuncTypes] = {}
		for at_type in reversed(_type.mro()):
			for key, attr in at_type.__dict__.items():
				if isinstance(attr, FuncTypes):
					_methods[key] = attr

		return _methods


def _resolve_type_from_str(type_str: str, via_module_path: str) -> type[Any]:
	"""文字列のタイプヒントを解析してタイプを解決

	Args:
		type_str (str): タイプヒント
		via_module_path (str): 由来のモジュールパス
	Returns:
		type[Any]: 解決したタイプ
	Note:
		* `eval`を使用して文字列からタイプを強引に解決する
		* ユーザー定義型は由来のモジュール内によって明示されているシンボルのみ解決が出来る
	"""
	module = import_module(via_module_path)
	depends = {key: symbol for key, symbol in module.__dict__.items() if not key.startswith('__')}
	return eval(type_str, depends)


T = TypeVar('T')


class Inspector:
	"""タイプヒントリゾルバー"""

	@classmethod
	def resolve(cls, origin: str | type[Any] | FuncTypes, via_module_path: str = '') -> Typehint:
		"""タイプヒントを解決

		Args:
			origin (str | type[Any] | FuncTypes): タイプ、関数オブジェクト、または文字列のタイプヒント
			via_module_path (str): 由来のモジュールパス。文字列のタイプヒントの場合のみ必須 (default = '')
		Returns:
			Typehint: タイプヒント
		"""
		actual_origin = cls.__to_actual_origin(origin, via_module_path)
		if isinstance(actual_origin, FuncTypes):
			return FunctionTypehint(actual_origin)
		elif cls.__is_scalar(actual_origin):
			return ScalarTypehint(actual_origin)
		else:
			return ClassTypehint(actual_origin)

	@classmethod
	def __to_actual_origin(cls, origin: str | type[Any] | FuncTypes, via_module_path: str) -> type[Any] | FuncTypes:
		"""指定のオリジンから解決可能なオリジンに変換

		Args:
			origin (str | type[Any] | FuncTypes): タイプ、関数オブジェクト、または文字列のタイプヒント
			via_module_path (str): 由来のモジュールパス。文字列のタイプヒントの場合のみ必須 (default = '')
		Returns:
			type[Any] | FuncTypes: オリジン
		Raises:
			ValueError: 由来が不明な場合に文字列のタイプヒントを使用
		"""
		if not isinstance(origin, str):
			return origin

		if len(via_module_path) == 0:
			raise ValueError(f'Unresolved origin type. via module is empty. origin: {origin}')

		return _resolve_type_from_str(origin, via_module_path)

	@classmethod
	def __is_scalar(cls, origin: type[Any]) -> bool:
		"""値型か判定

		Args:
			origin (type[Any]): タイプ
		Returns:
			bool: True = 値型
		"""
		if isinstance(origin, type) and issubclass(origin, (int, str, float, bool)):
			return True
		elif getattr(origin, '__origin__', origin) in [list, dict, tuple, type]:
			return True
		elif type(origin) in [UnionType, EnumType] or getattr(origin, '__origin__', origin) is Union:
			return True
		elif origin is None or origin is NoneType:
			return True
		else:
			return False
