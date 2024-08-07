from typing import Generic, TypeVar, cast

from rogw.tranp.lang.annotation import override

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
T_New = TypeVar('T_New')


class CVar(Generic[T_co]):
	"""C++型変数の互換クラス(基底)"""

	def __init__(self, origin: T_co) -> None:
		"""インスタンスを生成

		Args:
			origin (T_co): 実体のインスタンス
		"""
		self._origin: T_co | None = origin

	@property
	def on(self) -> T_co:
		"""実体を返却するリレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		return cast(T_co, self._origin)

	@property
	def raw(self) -> T_co:
		"""実体を返却する実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		return cast(T_co, self._origin)


class CP(CVar[T_co]):
	"""C++型変数の互換クラス(ポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CP[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CP[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@classmethod
	def new(cls, origin: T_New) -> 'CP[T_New]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`new`に相当"""
		return CP(origin)

	@property
	def ref(self) -> 'CRef[T_co]':
		"""参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRef(self.raw)

	@property
	def const(self) -> 'CPConst[T_co]':
		"""Constを返却する参照変換代替メソッド。C++では削除"""
		return CPConst(self.raw)

	def __add__(self, offset: int) -> int:
		"""アドレス演算(加算)

		Args:
			offset (int): オフセット
		Returns:
			int: アドレス
		"""
		return id(self) + offset

	def __sub__(self, other: 'CP[T_co]') -> int:
		"""アドレス演算(減算)

		Args:
			other (CP[T_co]): 対象
		Returns:
			int: アドレス
		"""
		return id(self) - id(other)


class CSP(CVar[T_co]):
	"""C++型変数の互換クラス(スマートポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSP[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CSP[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@override
	def __init__(self, origin: T_co | None = None) -> None:
		"""インスタンスを生成

		Args:
			origin (T_co | None): 実体のインスタンス (default = None)
		Note:
			XXX 空の状態を実現するため、スマートポインターのみNull許容型とする
			XXX 基底クラスのコンストラクターをシャドウイングしない方法を検討
		"""
		self._origin: T_co | None = origin

	@classmethod
	def empty(cls) -> 'CSP[T_co]':
		"""空のスマートポインターの初期化を代替するメソッド。C++では`std::shared_ptr<T>()`に相当"""
		return CSP[T_co]()

	@classmethod
	def new(cls, origin: T_New) -> 'CSP[T_New]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`std::make_shared`に相当"""
		return CSP(origin)

	@property
	def ref(self) -> 'CRef[T_co]':
		"""参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T_co]':
		"""ポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CP(self.raw)

	@property
	def const(self) -> 'CSPConst[T_co]':
		"""Constを返却する参照変換代替メソッド。C++では削除"""
		return CSPConst(self.raw)


class CRef(CVar[T_co]):
	"""C++型変数の互換クラス(参照)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRef[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRef[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def addr(self) -> 'CP[T_co]':
		"""ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)

	@property
	def const(self) -> 'CRefConst[T_co]':
		"""Constを返却する参照変換代替メソッド。C++では削除"""
		return CRefConst(self.raw)


class CPConst(CVar[T_co]):
	"""C++型変数の互換クラス(Constポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CPConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CPConst[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)


class CSPConst(CVar[T_co]):
	"""C++型変数の互換クラス(Constスマートポインター)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CSPConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CSPConst[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Constポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRefConst(CVar[T_co]):
	"""C++型変数の互換クラス(Const参照)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRefConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRefConst[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Constポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRawConst(CVar[T_co]):
	"""C++型変数の互換クラス(Const)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRawConst[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRefConst[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Constポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CPConst(self.raw)


class CRaw(CVar[T_co]):
	"""C++型変数の互換クラス(実体)"""

	@classmethod
	def __class_getitem__(cls, var_type: type[T]) -> 'type[CRaw[T]]':
		"""C++型変数でラップしたタイプを返却

		Args:
			var_type (type[T]): 実体の型
		Returns:
			type[CRaw[T]]: ラップした型
		"""
		return getattr(super(), '__class_getitem__')(var_type)

	@property
	def ref(self) -> 'CRef[T_co]':
		"""参照を返却する参照変換代替メソッド。C++では削除される"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T_co]':
		"""ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)
