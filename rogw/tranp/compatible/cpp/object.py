from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Generic, Self, TypeVar, override

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
T_New = TypeVar('T_New')


class CVar(Generic[T_co], metaclass=ABCMeta):
	"""C++型変数の互換クラス(抽象基底)"""

	@property
	@abstractmethod
	def on(self) -> T_co:
		"""Returns: 実体を返却 Note: リレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		...

	@property
	@abstractmethod
	def raw(self) -> T_co:
		"""Returns: 実体を返却 Note: 実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		...

	@property
	@abstractmethod
	def _origin_raw(self) -> T_co | None:
		"""Returns: 実体を返却 Note: 派生クラス用。C++としての役割は無い"""
		...

	def hex(self) -> str:
		"""アドレス値を取得

		Returns:
			アドレス値(16進数 ※先頭の'0x'は除外)
		"""
		return hex(id(self))[2:]

	def __eq__(self, other: Self) -> bool:
		"""比較演算子(==)のオーバーロード

		Args:
			other: 対象
		Returns:
			True = 一致
		"""
		return self.raw == other.raw

	def __ne__(self, other: Self) -> bool:
		"""比較演算子(!=)のオーバーロード

		Args:
			other: 対象
		Returns:
			True = 不一致
		"""
		return self.raw != other.raw

	def __hash__(self) -> int:
		"""ハッシュ値を取得

		Returns:
			ハッシュ値
		"""
		return id(self.raw)

	def __repr__(self) -> str:
		"""シリアライズ表現を取得

		Returns:
			シリアライズ表現
		"""
		return f'<{self.__class__.__name__}[{self._origin_raw.__class__.__name__}]: at {hex(id(self._origin_raw)).upper()} with {self._origin_raw}>'


class CVarNotNull(CVar[T_co]):
	"""C++型変数の互換クラス(Null安全型)

	Note:
		対象: CSP以外
	"""

	_origin: T_co

	def __init__(self, origin: T_co) -> None:
		"""インスタンスを生成

		Args:
			origin: 実体のインスタンス
		"""
		self._origin = origin

	@property
	@override
	def on(self) -> T_co:
		"""Returns: 実体を返却 Note: リレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		return self._origin

	@property
	@override
	def raw(self) -> T_co:
		"""Returns: 実体を返却 Note: 実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		return self._origin

	@property
	@override
	def _origin_raw(self) -> T_co:
		"""Returns: 実体を返却 Note: 派生クラス用。C++としての役割は無い"""
		return self._origin


class CVarNullable(CVar[T_co]):
	"""C++型変数の互換クラス(Null許容型)

	Note:
		```
		対象: CSPのみ
		XXX CSPのみ空の状態を表現するためNullを許容する
		```
	"""

	_origin: T_co | None

	def __init__(self, origin: T_co | None) -> None:
		"""インスタンスを生成

		Args:
			origin: 実体のインスタンス
		"""
		self._origin = origin

	@property
	@override
	def on(self) -> T_co:
		"""Returns: 実体を返却 Note: リレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		assert self._origin is not None, 'Origin is Null'
		return self._origin

	@property
	@override
	def raw(self) -> T_co:
		"""Returns: 実体を返却 Note: 実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		assert self._origin is not None, 'Origin is Null'
		return self._origin

	@property
	@override
	def _origin_raw(self) -> T_co | None:
		"""Returns: 実体を返却 Note: 派生クラス用。C++としての役割は無い"""
		return self._origin


class CP(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(ポインター)"""

	@classmethod
	def new(cls, origin: T_New) -> 'CP[T_New]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`new`に相当

		Args:
			origin: 実体のインタンス
		Returns:
			インスタンス
		"""
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
			offset: オフセット
		Returns:
			アドレス
		"""
		return id(self) + offset

	def __sub__(self, other: 'CP[T_co]') -> int:
		"""アドレス演算(減算)

		Args:
			other: 対象
		Returns:
			アドレス
		"""
		return id(self) - id(other)


class CSP(CVarNullable[T_co]):
	"""C++型変数の互換クラス(スマートポインター)"""

	@classmethod
	def empty(cls) -> 'CSP[T_co] | None':
		"""空のスマートポインターの初期化を代替するメソッド。C++では`std::shared_ptr<T>()`に相当

		Returns:
			インスタンス
		"""
		return CSP(None)

	@classmethod
	def new(cls, origin: T_New) -> 'CSP[T_New]':
		"""メモリを生成し、CPラップ型を返却するメモリ生成代替メソッド。C++では`std::make_shared`に相当

		Args:
			origin: 実体のインタンス
		Returns:
			インスタンス
		"""
		return CSP(origin)

	@property
	def ref(self) -> 'CRef[T_co]':
		"""Returns: 参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T_co]':
		"""Returns: ポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CP(self.raw)

	@property
	def const(self) -> 'CSPConst[T_co]':
		"""Returns: Constを返却する参照変換代替メソッド。C++では削除"""
		return CSPConst(self.raw)


class CRef(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(参照)"""

	@property
	def addr(self) -> 'CP[T_co]':
		"""Returns: ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)

	@property
	def const(self) -> 'CRefConst[T_co]':
		"""Returns: Constを返却する参照変換代替メソッド。C++では削除"""
		return CRefConst(self.raw)

	def copy(self, via: 'CRef[T_co]') -> None:
		"""代入コピー代替メソッド。C++では代入処理に置き換えられる

		Args:
			via: コピー元
		Note:
			```
			* 実体にコピーコンストラクターが実装されている場合はコピーコンストラクターを用いる
			* 実体にコピーコンストラクターがない場合は単に実体の置き換えを行う
			* PythonとC++ではコピーの性質が根本的に違い、完全な模倣はできないため、なるべくこの処理を用いないことを推奨
			```
		"""
		if hasattr(self._origin, '__py_copy__'):
			copy_origin: Callable[[CRef[T_co]], None] = getattr(self._origin, '__py_copy__')
			copy_origin(via)
		else:
			self._origin = via._origin


class CPConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(Constポインター)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)


class CSPConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(Constスマートポインター)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: Constポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRefConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(Const参照)"""

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: Constポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRawConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(Const)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: Const参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: Constポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CPConst(self.raw)


class CRaw(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(実体)"""

	@property
	def ref(self) -> 'CRef[T_co]':
		"""Returns: 参照を返却する参照変換代替メソッド。C++では削除される"""
		return CRef(self.raw)

	@property
	def addr(self) -> 'CP[T_co]':
		"""Returns: ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CP(self.raw)
