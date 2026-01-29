from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from enum import Enum, EnumType
from importlib import import_module
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Annotated, Any, ClassVar, ForwardRef, TypeAlias, TypeVar, Union, cast, get_origin

from rogw.tranp.lang.annotation import implements

FuncTypes: TypeAlias = FunctionType | MethodType | property | classmethod
T_Meta = TypeVar('T_Meta')


class FuncClasses(Enum):
	"""関数の種別"""
	ClassMethod = 'ClassMethod'
	Method = 'Method'
	Function = 'Function'


class Typehint(metaclass=ABCMeta):
	"""タイプヒント(基底クラス)"""

	@property
	@abstractmethod
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		...

	@property
	@abstractmethod
	def raw(self) -> type[Any] | FuncTypes | Callable:
		"""Returns: 元のタイプ"""
		...

	@abstractmethod
	def meta(self, meta_type: type[T_Meta]) -> T_Meta | None:
		"""メタ情報を取得

		Args:
			meta_type: メタ情報のタイプ
		Returns:
			メタ情報 | None
		Note:
			XXX メタ情報が引数の型として本質的に正しいか否かは保証しない
		"""
		...


class ScalarTypehint(Typehint):
	"""タイプヒント(値)

	Note:
		```
		### 対象のクラス
		* int/str/float/bool
		* list/dict/tuple/type
		* Union/UnionType
		* EnumType
		* None/NoneType
		```
	"""

	_type: type[Any]
	_meta: Any | None

	def __init__(self, scalar_type: type[Any], meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			scalar_type: タイプ
			meta: メタ情報 (default = None)
		"""
		self._type = scalar_type
		self._meta = meta

	@property
	@implements
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		if self.is_union:
			# XXX Union型の場合はUnionTypeを返却。UnionTypeはtypeと互換性が無いと判断されるため実装例に倣う @see types.py UnionType
			return type(int | str)
		else:
			return getattr(self._type, '__origin__', self._type)

	@property
	@implements
	def raw(self) -> type[Any]:
		"""Returns: 元のタイプ"""
		return self._type

	@implements
	def meta(self, meta_type: type[T_Meta]) -> T_Meta | None:
		"""メタ情報を取得

		Args:
			meta_type: メタ情報のタイプ
		Returns:
			メタ情報 | None
		Note:
			XXX メタ情報が引数の型として本質的に正しいか否かは保証しない
		"""
		return self._meta

	@property
	def is_null(self) -> bool:
		"""Returns: True = None"""
		return self._type is None or self._type is NoneType

	@property
	def is_generic(self) -> bool:
		"""Returns: True = ジェネリック型"""
		return getattr(self._type, '__origin__', self._type) in [list, dict, tuple, type]

	@property
	def is_union(self) -> bool:
		"""Returns: True = Union型"""
		return type(self._type) is UnionType or getattr(self._type, '__origin__', self._type) is Union

	@property
	def is_nullable(self) -> bool:
		"""Returns: True = Nullable型"""
		return self.is_union and type(None) in self.__sub_annos

	@property
	def is_enum(self) -> bool:
		"""Returns: True = Enum型"""
		return type(self._type) is EnumType

	@property
	def sub_types(self) -> list[Typehint]:
		"""Returns: ジェネリック/Union型のサブタイプのリスト"""
		return [Typehints.resolve(sub_type) for sub_type in self.__sub_annos]

	@property
	def __sub_annos(self) -> list[type[Any]]:
		"""Returns: ジェネリック/Union型のサブタイプのリスト"""
		return getattr(self._type, '__args__', [])

	@property
	def enum_members(self) -> list[Enum]:
		"""Returns: Enumのメンバー一覧"""
		return list(getattr(self.origin, '__members__').values())


class FunctionTypehint(Typehint):
	"""タイプヒント(関数)

	Note:
		```
		### 対象のクラス
		* 関数
		* メソッド(クラス/インスタンス)
		### 非対応
		* ラムダ ※タイプヒントが付けられないため
		```
	"""

	_func: FuncTypes | Callable
	_meta: Any | None

	def __init__(self, func: FuncTypes | Callable, meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			func: 関数オブジェクト
		Note:
			XXX コンストラクターはFuncTypeに当てはまらないため、Callableとして受け付ける
		"""
		self._func = func
		self._meta = meta

	@property
	@implements
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		return type(self._func)

	@property
	@implements
	def raw(self) -> FuncTypes | Callable:
		"""Returns: 関数オブジェクト"""
		return self._func

	@implements
	def meta(self, meta_type: type[T_Meta]) -> T_Meta | None:
		"""メタ情報を取得

		Args:
			meta_type: メタ情報のタイプ
		Returns:
			メタ情報 | None
		Note:
			XXX メタ情報が引数の型として本質的に正しいか否かは保証しない
		"""
		return self._meta

	@property
	def func_class(self) -> FuncClasses:
		"""関数の種別を取得

		Returns:
			関数の種別
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
		"""Returns: 引数リスト"""
		return {key: Typehints.resolve_internal(in_type, self.__via_module_path) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def returns(self) -> Typehint:
		"""Returns: 戻り値"""
		return Typehints.resolve_internal(self.__annos['return'], self.__via_module_path)

	@property
	def __via_module_path(self) -> str:
		"""Returns: 関数由来のモジュールパス"""
		if isinstance(self._func, property):
			# propertyは`__module__`が無いため、元の関数オブジェクトを通して取得する
			return getattr(self._func, 'fget').__module__
		else:
			return self._func.__module__

	@property
	def __annos(self) -> dict[str, type[Any]]:
		"""Returns: タイプヒントのリスト"""
		if isinstance(self._func, property):
			# propertyは`__annotations__`が無いため、元の関数オブジェクトを通して取得する
			return getattr(self._func, 'fget').__annotations__
		else:
			return self._func.__annotations__


class ClassTypehint(Typehint):
	"""タイプヒント(クラス)

	Note:
		```
		### 対象のクラス
		* クラス全般
		### 留意事項
		* クラス・インスタンス変数どちらもクラスの`__annotations__`から抽出
		* クラス変数: ClassVarで明示
		* インスタンス変数: ClassVar以外
		```
	"""

	_type: type[Any]
	_meta: Any | None

	def __init__(self, class_type: type[Any], meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			class_type: クラス
		"""
		self._type = class_type
		self._meta = meta

	@property
	@implements
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		return getattr(self._type, '__origin__', self._type)

	@property
	@implements
	def raw(self) -> type[Any]:
		"""Returns: 元のタイプ"""
		return self._type

	@implements
	def meta(self, meta_type: type[T_Meta]) -> T_Meta | None:
		"""メタ情報を取得

		Args:
			meta_type: メタ情報のタイプ
		Returns:
			メタ情報 | None
		Note:
			XXX メタ情報が引数の型として本質的に正しいか否かは保証しない
		"""
		return self._meta

	@property
	def is_generic(self) -> bool:
		"""Returns: True = ジェネリック型"""
		return hasattr(self._type, '__origin__')

	@property
	def sub_types(self) -> list[Typehint]:
		"""Returns: ジェネリック型のサブタイプのリスト"""
		sub_annos: list[type[Any]] = getattr(self._type, '__args__', [])
		return [Typehints.resolve_internal(sub_type, self._type.__module__) for sub_type in sub_annos]

	@property
	def constructor(self) -> FunctionTypehint:
		"""Returns: コンストラクター"""
		return FunctionTypehint(self._type.__init__)

	@property
	def methods(self) -> dict[str, FunctionTypehint]:
		"""Returns: メソッド一覧"""
		return {key: FunctionTypehint(prop) for key, prop in self.__recursive_methods(self._type).items()}

	def class_vars(self, lookup_private: bool = True) -> dict[str, Typehint]:
		"""クラス変数の一覧を取得

		Args:
			lookup_private: True = プライベート変数を抽出 (default = True)
		Returns:
			クラス変数一覧
		"""
		annos = {key: anno for key, anno in self.__recursive_annos(self._type, lookup_private, for_class_var=True).items()}
		return {key: Typehints.resolve_internal(attr, self._type.__module__) for key, attr in annos.items()}

	def self_vars(self, lookup_private: bool = True) -> dict[str, Typehint]:
		"""インスタンス変数の一覧を取得

		Args:
			lookup_private: True = プライベート変数を抽出 (default = True)
		Returns:
			インスタンス変数一覧
		"""
		annos = {key: anno for key, anno in self.__recursive_annos(self._type, lookup_private, for_class_var=False).items()}
		return {key: Typehints.resolve_internal(attr, self._type.__module__) for key, attr in annos.items()}

	def __recursive_annos(self, a_type: type[Any], lookup_private: bool, for_class_var: bool) -> dict[str, type[Any]]:
		"""クラス階層を辿ってアノテーションを収集

		Args:
			a_type: タイプ
			lookup_private: True = プライベート変数を抽出
			for_class_var: True = クラス変数のみ抽出, False = インスタンス変数のみ抽出
		Returns:
			アノテーション一覧
		"""
		annos: dict[str, type[Any]] = {}
		for at_type in reversed(a_type.mro()):
			in_annos: dict[str, type[Any]] = getattr(at_type, '__annotations__', {})
			for key, anno in in_annos.items():
				if not lookup_private and key.startswith(f'_{at_type.__name__}__'):
					continue

				is_class_var = getattr(anno, '__origin__', anno) is ClassVar
				if (for_class_var and not is_class_var) or (not for_class_var and is_class_var):
					continue

				origin, meta = OriginUnpacker.unpack(anno, at_type.__module__)
				# FIXME 型の不一致は一旦castで対処
				# XXX メタ情報が含まれる場合はAnnotatedを復元
				if meta:
					annos[key] = cast(type, Annotated[origin, meta])
				else:
					annos[key] = cast(type, origin)

		return annos

	def __recursive_methods(self, a_type: type[Any]) -> dict[str, FuncTypes]:
		"""クラス階層を辿ってメソッドを収集

		Args:
			a_type: タイプ
		Returns:
			メソッド一覧
		"""
		_methods: dict[str, FuncTypes] = {}
		for at_type in reversed(a_type.mro()):
			for key, attr in at_type.__dict__.items():
				if isinstance(attr, FuncTypes):
					_methods[key] = attr

		return _methods


class OriginUnpacker:
	"""オリジンアンパッカー"""

	@classmethod
	def unpack(cls, origin: type[Any] | FuncTypes | str | ForwardRef, via_module_path: str) -> tuple[type[Any] | FuncTypes, Any | None]:
		"""オリジンからタイプ・メタ情報をアンパック

		Args:
			origin: オリジン(タイプ/関数オブジェクト/文字列/ForwardRef)
			via_module_path: 由来のモジュールパス。文字列のタイプヒントの解析に使用
		Returns:
			(タイプ, メタ情報)
		Note:
			Annotated/ForwardRefは型情報として意味を成さないので暗黙的にアンパック
		"""
		if isinstance(origin, str):
			return OriginUnpacker.forward_to_type(origin, via_module_path), None
		elif get_origin(origin) is Annotated:
			_origin = getattr(origin, '__origin__')
			# FIXME 可変長tupleは扱いにくいため、一旦先頭要素のみ使用
			meta: Any = getattr(origin, '__metadata__')[0]
			if type(_origin) is ForwardRef:
				return OriginUnpacker.forward_to_type(_origin.__forward_arg__, via_module_path), meta
			else:
				return _origin, meta
		elif get_origin(origin) is ClassVar:
			_origin = getattr(origin, '__args__')[0]
			if type(_origin) is ForwardRef:
				return OriginUnpacker.forward_to_type(_origin.__forward_arg__, via_module_path), None
			else:
				return _origin, None
		elif type(origin) is ForwardRef:
			return OriginUnpacker.forward_to_type(origin.__forward_arg__, via_module_path), None
		else:
			return origin, None

	@classmethod
	def forward_to_type(cls, type_str: str, via_module_path: str) -> type[Any]:
		"""文字列のタイプヒントを解析してタイプを解決

		Args:
			type_str: タイプの文字列
			via_module_path: 由来のモジュールパス
		Returns:
			解決したタイプ
		Raises:
			ValueError: 由来のモジュールパスが不正
		Note:
			```
			* `eval`を使用して文字列からタイプを強引に解決する
			* ユーザー定義型は由来のモジュール内によって明示されているシンボルのみ解決が出来る
			```
		"""
		if len(via_module_path) == 0:
			raise ValueError(f'Unresolved origin type. via module is empty. origin: {type_str}')

		module = import_module(via_module_path)
		depends = {key: symbol for key, symbol in module.__dict__.items() if not key.startswith('__')}
		return eval(type_str, depends)


class Typehints:
	"""タイプヒントリゾルバー"""

	@classmethod
	def resolve(cls, origin: str | type[Any] | FuncTypes) -> Typehint:
		"""タイプヒントを解決

		Args:
			origin: タイプ、関数オブジェクト、または文字列のタイプヒント
		Returns:
			タイプヒント
		"""
		return cls.__resolve_impl(origin, '')

	@classmethod
	def resolve_internal(cls, origin: str | type[Any] | FuncTypes, via_module_path: str) -> Typehint:
		"""タイプヒントを解決(クラス/関数の内部オブジェクト用)

		Args:
			origin: タイプ、関数オブジェクト、または文字列のタイプヒント
			via_module_path: 由来のモジュールパス。文字列のタイプヒントの解析に使用
		Returns:
			タイプヒント
		"""
		return cls.__resolve_impl(origin, via_module_path)

	@classmethod
	def __resolve_impl(cls, origin: str | type[Any] | FuncTypes, via_module_path: str) -> Typehint:
		"""タイプヒントを解決

		Args:
			origin: タイプ、関数オブジェクト、または文字列のタイプヒント
			via_module_path: 由来のモジュールパス。文字列のタイプヒントの解析に使用
		Returns:
			タイプヒント
		"""
		actual_origin, meta = OriginUnpacker.unpack(origin, via_module_path)
		if isinstance(actual_origin, FuncTypes):
			return FunctionTypehint(actual_origin, meta)
		elif cls.__is_scalar(actual_origin):
			return ScalarTypehint(actual_origin, meta)
		else:
			return ClassTypehint(actual_origin, meta)

	@classmethod
	def __is_scalar(cls, origin: type[Any]) -> bool:
		"""値型か判定

		Args:
			origin: タイプ
		Returns:
			True = 値型
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
