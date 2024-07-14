from enum import Enum, EnumType
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Any, Callable

from rogw.tranp.lang.annotation import override
from rogw.tranp.lang.comment import Comment


class Annotation:
	"""アノテーション(基底クラス)"""

	@property
	def origin(self) -> type:
		"""type: メインタイプ"""
		...


class ScalarAnnotation(Annotation):
	"""アノテーション(値)

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
	def sub_types(self) -> list[Annotation]:
		"""list[Annotation]: ジェネリック/Union型のサブタイプのリスト"""
		return [AnnotationResolver.resolve(sub_type) for sub_type in self.__sub_annos]

	@property
	def __sub_annos(self) -> list[type]:
		"""list[type]: ジェネリック/Union型のサブタイプのリスト"""
		return getattr(self._type, '__args__', [])

	@property
	def enum_members(self) -> list[Enum]:
		"""dict[str, Enum]: Enumのメンバー一覧"""
		return list(getattr(self.origin, '__members__').values())


class FunctionAnnotation(Annotation):
	"""アノテーション(関数)

	Note:
		### 対象のクラス
		* 関数
		* メソッド(クラス/インスタンス)
		### 非対応
		* ラムダ ※アノテーションが付けられないため
	"""

	def __init__(self, func_or_class: Callable) -> None:
		"""インスタンスを生成

		Args:
			func_or_class (Callable): 関数・メソッド・クラス
		Note:
			クラスを指定した場合は暗黙的にコンストラクターを展開する
		"""
		self._func = func_or_class if isinstance(func_or_class, (FunctionType, MethodType)) else func_or_class.__init__

	@property
	@override
	def origin(self) -> type:
		"""type: メインタイプ"""
		return type(self._func)

	@property
	def raw(self) -> Callable:
		"""Callable: 元の型"""
		return self._func

	@property
	def is_static(self) -> bool:
		"""bool: True = クラスメソッド"""
		return isinstance(getattr(self._func, '__self__', None), type)

	@property
	def is_method(self) -> bool:
		"""bool: True = メソッド"""
		return isinstance(self._func, MethodType)

	@property
	def is_function(self) -> bool:
		"""bool: True = 関数"""
		return isinstance(self._func, FunctionType)

	@property
	def receiver(self) -> Any:
		"""メソッドレシーバーを返却。取得の成否、及び取得対象は生成元に依存する

		Returns:
			Any: メソッドレシーバー
		Note:
			### クラスから生成した場合
			* クラスメソッド: クラス
			* インスタンスメソッド: NG
			### インスタンスから生成した場合
			* クラスメソッド: クラス
			* インスタンスメソッド: インスタンス
		Raises:
			TypeError: 関数、または取得できない条件で使用
		"""
		return getattr(self._func, '__self__')

	@property
	def args(self) -> dict[str, Annotation]:
		"""dict[str, Annotation]: 引数リスト"""
		return {key: AnnotationResolver.resolve(in_type) for key, in_type in self.__annos.items() if key != 'return'}

	@property
	def returns(self) -> Annotation:
		"""Annotation: 戻り値"""
		return AnnotationResolver.resolve(self.__annos['return'])

	@property
	def __annos(self) -> dict[str, type]:
		"""dict[str, type]: アノテーションのリスト"""
		return self._func.__annotations__


class ClassAnnotation(Annotation):
	"""アノテーション(クラス)

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
	def constructor(self) -> FunctionAnnotation:
		"""FunctionAnnotation: コンストラクター"""
		return FunctionAnnotation(self._type.__init__)

	@property
	def class_vars(self) -> dict[str, Annotation]:
		"""クラス変数の一覧を取得

		Returns:
			dict[str, Annotation]: クラス変数一覧
		Note:
			Pythonではクラス変数とインスタンス変数の差が厳密ではないため、
			このクラスではクラス直下に定義された変数をクラス変数と位置づける
		"""
		annos = {key: AnnotationResolver.resolve(prop) for key, prop in self.__recursive_annos(self._type).items()}
		return {key: prop for key, prop in annos.items() if prop is not FunctionAnnotation}

	def __recursive_annos(self, _type: type) -> dict[str, type]:
		"""クラス階層を辿ってアノテーションを収集

		Args:
			_type (type): タイプ
		Returns:
			dict[str, type]: アノテーション一覧
		"""
		annos: dict[str, type] = {}
		for inherit in reversed(_type.mro()):
			annos = {**annos, **getattr(inherit, '__annotations__', {})}

		return annos

	@property
	def self_vars(self) -> dict[str, Annotation]:
		"""インスタンス変数の一覧を取得

		Returns:
			dict[str, Annotation]: インスタンス変数一覧
		Note:
			Pythonでは、クラスからインスタンス変数を確実に抜き出す方法が無いため、
			クラスに記入されたDocStringを基にインスタンス変数のアノテーションを生成する
		"""
		docstrings = [Comment.parse(doc) for doc in self.__recursive_docs(self._type)]
		var_types: dict[str, type] = {}
		for docstring in docstrings:
			var_types = {**var_types, **{attr.name: eval(attr.type) for attr in docstring.attributes}}

		return {key: AnnotationResolver.resolve(prop) for key, prop in var_types.items()}

	def __recursive_docs(self, _type: type) -> list[str]:
		"""クラス階層を辿ってDocStringを収集

		Args:
			_type (type): タイプ
		Returns:
			list[str]: DocStringのリスト
		"""
		docs: list[str] = [getattr(inherit, '__doc__') for inherit in reversed(_type.mro()) if hasattr(inherit, '__doc__')]
		return [doc for doc in docs if doc]

	@property
	def methods(self) -> dict[str, FunctionAnnotation]:
		"""dict[str, FunctionAnnotation]: メソッド一覧"""
		return {key: FunctionAnnotation(prop) for key, prop in self.__recursive_methods(self._type).items()}

	def __recursive_methods(self, _type: type) -> dict[str, FunctionType | MethodType]:
		"""クラス階層を辿ってメソッドを収集

		Args:
			_type (type): タイプ
		Returns:
			dict[str, FunctionType | MethodType]: メソッド一覧
		"""
		_methods: dict[str, FunctionType | MethodType] = {}
		for inherit in reversed(_type.mro()):
			for key in inherit.__dict__.keys():
				# XXX getattrで取得する ※__dict__の値が想定外の型になるため
				attr = getattr(inherit, key)
				if isinstance(attr, (FunctionType, MethodType)):
					_methods[key] = attr

		return _methods


class AnnotationResolver:
	"""アノテーションリゾルバー"""

	@classmethod
	def resolve(cls, origin: type | FunctionType | MethodType) -> Annotation:
		"""アノテーションを解決

		Args:
			origin (type | FunctionType | MethodType): タイプ
		Returns:
			Annotation: アノテーション
		"""
		if isinstance(origin, (FunctionType, MethodType)):
			return FunctionAnnotation(origin)
		elif cls.__is_scalar(origin):
			return ScalarAnnotation(origin)
		else:
			return ClassAnnotation(origin)

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
