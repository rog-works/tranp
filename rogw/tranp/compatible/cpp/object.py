from typing import Generic, TypeVar

from rogw.tranp.compatible.python.embed import __hint_generic__

T = TypeVar('T')


class CVar(Generic[T]):
	"""C++型変数の互換クラス(基底)"""

	def __init__(self, origin: T) -> None:
		"""インスタンスを生成

		Args:
			origin (T): 実体のインスタンス
		"""
		self.__origin = origin

	@property
	def on(self) -> T:
		"""実体を返却するリレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		return self.__origin

	@property
	def raw(self) -> T:
		"""実体を返却する実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		return self.__origin


@__hint_generic__(T)
class CP(CVar[T]):
	"""C++型変数の互換クラス(ポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CP[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CP[T]]: ラップした型
		"""
		return CP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CP[T]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`new`に相当"""
		return cls(origin)

	@property
	def ref(self) -> 'CRef[T]':
		"""参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRef(self.raw)

	@property
	def const(self) -> 'CPConst[T]':
		"""Constを返却する参照変換代替メソッド。C++では削除"""
		return CPConst(self.raw)


@__hint_generic__(T)
class CSP(CVar[T]):
	"""C++型変数の互換クラス(スマートポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSP[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CSP[T]]: ラップした型
		"""
		return CSP[var_type]

	@classmethod
	def new(cls, origin: T) -> 'CSP[T]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`std::make_shared`に相当"""
		return cls(origin)

	@property
	def ref(self) -> 'CRef[T]':
		"""参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T]':
		"""ポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CP(self.raw)


@__hint_generic__(T)
class CRef(CVar[T]):
	"""C++型変数の互換クラス(参照)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRef[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRef[T]]: ラップした型
		"""
		return CRef[var_type]

	@property
	def addr(self) -> 'CP[T]':
		"""ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)

	@property
	def const(self) -> 'CRefConst[T]':
		"""Constを返却する参照変換代替メソッド。C++では削除"""
		return CRefConst(self.raw)


@__hint_generic__(T)
class CPConst(CVar[T]):
	"""C++型変数の互換クラス(Constポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CPConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CPConst[T]]: ラップした型
		"""
		return CPConst[var_type]

	@property
	def ref(self) -> 'CRefConst[T]':
		"""Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)


@__hint_generic__(T)
class CRefConst(CVar[T]):
	"""C++型変数の互換クラス(Const参照)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRefConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRefConst[T]]: ラップした型
		"""
		return CRefConst[var_type]

	@property
	def addr(self) -> 'CPConst[T]':
		"""Constポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


@__hint_generic__(T)
class CRaw(CVar[T]):
	"""C++型変数の互換クラス(実体)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRaw[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRaw[T]]: ラップした型
		"""
		return CRaw[var_type]

	@property
	def ref(self) -> 'CRef[T]':
		"""参照を返却する参照変換代替メソッド。C++では削除される"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T]':
		"""ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)
