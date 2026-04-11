from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from enum import Enum, EnumType
from importlib import import_module
from inspect import signature as inspect_signature
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Annotated, Any, ClassVar, ForwardRef, TypeAlias, Union, cast, get_origin, override

FuncTypes: TypeAlias = FunctionType | MethodType | property | classmethod


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
	def meta[T](self, meta_type: type[T]) -> T | None:
		"""メタ情報を取得

		Args:
			meta_type: メタ情報のタイプ
		Returns:
			メタ情報 | None
		Note:
			XXX メタ情報が引数の型として本質的に正しいか否かは保証しない
		"""
		...

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{self.raw.__name__}]: at 0x{hex(id(self))[2:].upper()}>'


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

	_raw: type[Any]
	_meta: Any | None

	def __init__(self, scalar_type: type[Any], meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			scalar_type: タイプ
			meta: メタ情報 (default = None)
		"""
		self._raw = scalar_type
		self._meta = meta

	@property
	@override
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		if self.is_union:
			# XXX Union型の場合はUnionTypeを返却。UnionTypeはtypeと互換性が無いと判断されるため実装例に倣う @see types.py UnionType
			return type(int | str)
		else:
			return getattr(self._raw, '__origin__', self._raw)

	@property
	@override
	def raw(self) -> type[Any]:
		"""Returns: 元のタイプ"""
		return self._raw

	@override
	def meta[T](self, meta_type: type[T]) -> T | None:
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
		return self._raw is None or self._raw is NoneType

	@property
	def is_generic(self) -> bool:
		"""Returns: True = ジェネリック型"""
		return getattr(self._raw, '__origin__', self._raw) in [list, dict, tuple, type]

	@property
	def is_union(self) -> bool:
		"""Returns: True = Union型"""
		return type(self._raw) is UnionType or getattr(self._raw, '__origin__', self._raw) is Union

	@property
	def is_nullable(self) -> bool:
		"""Returns: True = Nullable型"""
		return self.is_union and type(None) in self.__sub_annos

	@property
	def is_enum(self) -> bool:
		"""Returns: True = Enum型"""
		return type(self._raw) is EnumType

	@property
	def sub_types(self) -> list[Typehint]:
		"""Returns: ジェネリック/Union型のサブタイプのリスト"""
		return [Typehints.resolve(sub_type) for sub_type in self.__sub_annos]

	@property
	def __sub_annos(self) -> list[type[Any]]:
		"""Returns: ジェネリック/Union型のサブタイプのリスト"""
		return getattr(self._raw, '__args__', [])

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

	_raw: FuncTypes | Callable
	_meta: Any | None

	def __init__(self, func: FuncTypes | Callable, meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			func: 関数オブジェクト
		Note:
			XXX コンストラクターはFuncTypesに当てはまらないため、Callableとして受け付ける
		"""
		self._raw = func
		self._meta = meta

	@property
	@override
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		return type(self._raw)

	@property
	@override
	def raw(self) -> FuncTypes | Callable:
		"""Returns: 元のタイプ"""
		return self._raw

	@override
	def meta[T](self, meta_type: type[T]) -> T | None:
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
	def func(self) -> FuncTypes | Callable:
		"""Returns: 関数オブジェクト"""
		return getattr(self._raw, 'fget') if self.origin is property else self._raw

	@property
	def func_class(self) -> FuncClasses:
		"""関数の種別を取得

		Returns:
			関数の種別
		Note:
			XXX Pythonではメソッドはオブジェクトに動的にバインドされるため、タイプから関数オブジェクトを取得した場合、メソッドとして判定する方法がない ※Pythonの仕様
		"""
		if self.origin is classmethod or isinstance(getattr(self._raw, '__self__', None), type):
			return FuncClasses.ClassMethod
		elif self.origin in [MethodType, property]:
			return FuncClasses.Method
		else:
			return FuncClasses.Function

	@property
	def params(self) -> dict[str, Typehint]:
		"""Returns: 仮引数一覧"""
		return {key: Typehints.resolve_internal(in_type, self.__via_module_path) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def returns(self) -> Typehint:
		"""Returns: 戻り値"""
		return Typehints.resolve_internal(self.__annos['return'], self.__via_module_path)

	@property
	def default_params(self) -> dict[str, Any | None]:
		"""Returns: デフォルト引数一覧"""
		defaults: dict[str, Any | None] = {}
		# XXX castで警告を抑制
		parameters = inspect_signature(cast(type, self.func)).parameters
		for key, param in parameters.items():
			# XXX inspectの内部クラス`_empty`がデフォルト引数無しを表す
			if getattr(param.default, '__name__', '') != '_empty':
				defaults[key] = param.default

		return defaults

	@property
	def __via_module_path(self) -> str:
		"""Returns: 関数由来のモジュールパス"""
		return self.func.__module__

	@property
	def __annos(self) -> dict[str, type[Any]]:
		"""Returns: タイプヒントのリスト"""
		return self.func.__annotations__


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

	_raw: type[Any]
	_meta: Any | None

	def __init__(self, class_type: type[Any], meta: Any | None = None) -> None:
		"""インスタンスを生成

		Args:
			class_type: クラス
		"""
		self._raw = class_type
		self._meta = meta

	@property
	@override
	def origin(self) -> type[Any]:
		"""Returns: メインタイプ"""
		return getattr(self._raw, '__origin__', self._raw)

	@property
	@override
	def raw(self) -> type[Any]:
		"""Returns: 元のタイプ"""
		return self._raw

	@override
	def meta[T](self, meta_type: type[T]) -> T | None:
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
		return hasattr(self._raw, '__origin__')

	@property
	def inherits(self) -> list[Typehint]:
		"""Returns: 継承タイプリスト"""
		return [Typehints.resolve_internal(inherit, self._raw.__module__) for inherit in self.origin.__bases__]

	@property
	def sub_types(self) -> list[Typehint]:
		"""Returns: ジェネリック型のサブタイプのリスト"""
		sub_annos: list[type[Any]] = getattr(self._raw, '__args__', [])
		return [Typehints.resolve_internal(sub_type, self._raw.__module__) for sub_type in sub_annos]

	@property
	def constructor(self) -> FunctionTypehint:
		"""Returns: コンストラクター"""
		return FunctionTypehint(self._raw.__init__)

	def methods(self, with_inherit: bool = True, with_private: bool = False, with_special: bool = False) -> dict[str, FunctionTypehint]:
		"""メソッド一覧を取得

		Args:
			with_inherit: True = 継承チェーンを再帰的に抽出 (default = True)
			with_private: True = プライベートを抽出 (default = False)
			with_special: True = 特殊メソッドを抽出 (default = False)
		Returns:
			メソッド一覧
		"""
		methods = self.__lookup_methods(*self.__method_lookup_info(with_inherit, with_private, with_special))
		return {key: FunctionTypehint(prop) for key, prop in methods.items()}

	def class_vars(self, with_inherit: bool = True, with_private: bool = False) -> dict[str, Typehint]:
		"""クラス変数一覧を取得

		Args:
			with_inherit: True = 継承チェーンを再帰的に抽出 (default = True)
			with_private: True = プライベートを抽出 (default = False)
		Returns:
			クラス変数一覧
		"""
		vars = self.__lookup_vars(*self.__var_lookup_info(with_inherit, with_private, for_class_var=True))
		return {key: Typehints.resolve_internal(attr, self._raw.__module__) for key, attr in vars.items()}

	def self_vars(self, with_inherit: bool = True, with_private: bool = False) -> dict[str, Typehint]:
		"""インスタンス変数一覧を取得

		Args:
			with_inherit: True = 継承チェーンを再帰的に抽出 (default = True)
			with_private: True = プライベートを抽出 (default = False)
		Returns:
			インスタンス変数一覧
		"""
		vars = self.__lookup_vars(*self.__var_lookup_info(with_inherit, with_private, for_class_var=False))
		return {key: Typehints.resolve_internal(attr, self._raw.__module__) for key, attr in vars.items()}

	def __method_lookup_info(self, with_inherit: bool, with_private: bool, with_special: bool) -> tuple[list[type[Any]], Callable[[type[Any], str, Any], bool]]:
		"""ルックアップ情報を生成(メソッド用)

		Args:
			with_inherit: True = 継承チェーンを再帰的に抽出
			with_private: True = プライベートを抽出
			with_special: True = 特殊メソッドを抽出
		Returns:
			(タイプリスト, 出力判定関数)
		"""
		to_allowed = {
			(True, True): self.__allow_method_all,
			(True, False): self.__allow_method_general,
			(False, True): self.__allow_method_expose,
			(False, False): self.__allow_method_expose_general,
		}
		each_types = self.__recursive_types() if with_inherit else self.__self_types()
		return each_types, to_allowed[with_private, with_special]

	def __allow_method_all(self, a_type: type[Any], key: str, attr: Any) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, attr: 属性 Returns: True = 出力対象"""
		return isinstance(attr, FuncTypes)

	def __allow_method_general(self, a_type: type[Any], key: str, attr: Any) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, attr: 属性 Returns: True = 出力対象"""
		return isinstance(attr, FuncTypes) and not self.__is_special_method(key)

	def __allow_method_expose(self, a_type: type[Any], key: str, attr: Any) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, attr: 属性 Returns: True = 出力対象"""
		return isinstance(attr, FuncTypes) and not self.__is_private_attr(a_type, key)

	def __allow_method_expose_general(self, a_type: type[Any], key: str, attr: Any) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, attr: 属性 Returns: True = 出力対象"""
		return isinstance(attr, FuncTypes) and not self.__is_private_attr(a_type, key) and not self.__is_special_method(key)
	
	def __var_lookup_info(self, with_inherit: bool, with_private: bool, for_class_var: bool) -> tuple[list[type[Any]], Callable[[type[Any], str, type[Any]], bool]]:
		"""ルックアップ情報を生成(変数用)

		Args:
			with_inherit: True = 継承チェーンを再帰的に抽出
			with_private: True = プライベートを抽出
			for_class_var: True = クラス変数のみ抽出, False = インスタンス変数のみ抽出
		Returns:
			(タイプリスト, 出力判定関数)
		"""
		to_allowed = {
			(True, True): self.__allow_class_var_all,
			(True, False): self.__allow_self_var_all,
			(False, True): self.__allow_class_var_expose,
			(False, False): self.__allow_self_var_expose,
		}
		each_types = self.__recursive_types() if with_inherit else self.__self_types()
		return each_types, to_allowed[(with_private, for_class_var)]
	
	def __allow_class_var_all(self, a_type: type[Any], key: str, anno: type[Any]) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, anno: アノテーション Returns: True = 出力対象"""
		return self.__is_class_var(anno)

	def __allow_self_var_all(self, a_type: type[Any], key: str, anno: type[Any]) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, anno: アノテーション Returns: True = 出力対象"""
		return not self.__is_class_var(anno)

	def __allow_class_var_expose(self, a_type: type[Any], key: str, anno: type[Any]) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, anno: アノテーション Returns: True = 出力対象"""
		return not self.__is_private_attr(a_type, key) and self.__is_class_var(anno)

	def __allow_self_var_expose(self, a_type: type[Any], key: str, anno: type[Any]) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名, anno: アノテーション Returns: True = 出力対象"""
		return not self.__is_private_attr(a_type, key) and not self.__is_class_var(anno)

	def __self_types(self) -> list[type[Any]]:
		"""Returns: タイプリスト(自身のみ)"""
		return [self._raw]

	def __recursive_types(self) -> list[type[Any]]:
		"""Returns: タイプリスト(自身 + 継承チェーン)"""
		return list(reversed(self._raw.mro()))

	def __is_private_attr(self, a_type: type[Any], key: str) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名 Returns: True = プライベート"""
		return key.startswith(f'_{a_type.__name__}__')

	def __is_special_method(self, key: str) -> bool:
		"""Args: key: 属性名 Returns: True = 特殊メソッド"""
		return key.startswith('__') and key.endswith('__')

	def __is_class_var(self, anno: type[Any]) -> bool:
		"""Args: a_type: 保有クラス, key: 属性名 Returns: True = クラス変数"""
		return getattr(anno, '__origin__', anno) is ClassVar

	def __lookup_methods(self, each_types: list[type[Any]], allowed: Callable[[type[Any], str, Any], bool]) -> dict[str, FuncTypes]:
		"""クラス階層を辿ってメソッドを収集

		Args:
			each_types: タイプリスト
			allowed: 出力判定関数
		Returns:
			メソッド一覧
		"""
		_methods: dict[str, FuncTypes] = {}
		for at_type in each_types:
			for key, attr in at_type.__dict__.items():
				if allowed(at_type, key, attr):
					_methods[key] = attr

		return _methods

	def __lookup_vars(self, each_types: list[type[Any]], allowed: Callable[[type[Any], str, type[Any]], bool]) -> dict[str, type[Any]]:
		"""クラス階層を辿って変数を収集

		Args:
			each_types: タイプリスト
			allowed: 出力判定関数
		Returns:
			変数一覧
		"""
		vars: dict[str, type[Any]] = {}
		for at_type in each_types:
			in_annos: dict[str, type[Any]] = getattr(at_type, '__annotations__', {})
			for key, anno in in_annos.items():
				if not allowed(at_type, key, anno):
					continue

				origin, meta = OriginUnpacker.unpack(anno, at_type.__module__)
				# FIXME 型の不一致は一旦castで対処
				# XXX メタ情報が含まれる場合はAnnotatedを復元
				if meta is not None:
					vars[key] = cast(type, Annotated[origin, meta])
				else:
					vars[key] = cast(type, origin)

		return vars


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
			return cls.forward_to_type(origin, via_module_path), None
		elif get_origin(origin) is Annotated:
			_origin = getattr(origin, '__origin__')
			# FIXME 可変長tupleは扱いにくいため、一旦先頭要素のみ使用
			meta: Any = getattr(origin, '__metadata__')[0]
			if type(_origin) is ForwardRef:
				return cls.forward_to_type(_origin.__forward_arg__, via_module_path), meta
			else:
				return _origin, meta
		elif get_origin(origin) is ClassVar:
			_origin = getattr(origin, '__args__')[0]
			if type(_origin) is ForwardRef:
				return cls.forward_to_type(_origin.__forward_arg__, via_module_path), None
			else:
				return _origin, None
		elif type(origin) is ForwardRef:
			return cls.forward_to_type(origin.__forward_arg__, via_module_path), None
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
