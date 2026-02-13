from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Generic, Self, TypeVar, override
from weakref import ReferenceType

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

	def to_addr_id(self) -> int:
		"""アドレス値を取得

		Returns:
			アドレス値
		"""
		return self.__hash__()

	def to_addr_hex(self) -> str:
		"""アドレス値を取得

		Returns:
			アドレス値(16進数 ※先頭の'0x'は除外)
		"""
		return hex(self.__hash__())[2:].upper()

	def __eq__(self, other: Self | None) -> bool:
		"""比較演算子(==)のオーバーロード

		Args:
			other: 対象
		Returns:
			True = 一致
		"""
		return other is not None and self.__hash__() == other.__hash__()

	def __ne__(self, other: Self | None) -> bool:
		"""比較演算子(!=)のオーバーロード

		Args:
			other: 対象
		Returns:
			True = 不一致
		"""
		return not self.__eq__(other)

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
		return f'<{self.__class__.__name__}[{self._origin_raw.__class__.__name__}]: at 0x{self.to_addr_hex()} with {self._origin_raw}>'


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

	def __init__(self, origin_at: CVarNotNull[T_co] | None) -> None:
		"""インスタンスを生成

		Args:
			origin_at: 実体のポインター
		"""
		self._origin = origin_at.raw if origin_at else None

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
		"""メモリを生成し、ポインター型を返却するメモリ生成代替メソッド。C++では`new`に相当

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

	def __getitem__(self, key: str | int) -> 'CP[T_co]':
		"""配下要素の取得

		Args:
			key: キー
		Returns:
			配下要素
		Note:
			```
			* 自己再帰的な構造を持つコレクション用のインデクサー
			* XXX このメソッドは利便性のみを着眼点とし、C++の標準仕様と全く関係ない点に注意
			```
		"""
		return getattr(self.raw, '__getitem__')(key)


class CSP(CVarNullable[T_co]):
	"""C++型変数の互換クラス(共有ポインター)"""

	@classmethod
	def empty(cls) -> 'CSP[T_co] | None':
		"""空の共有ポインターの初期化を代替するメソッド。C++では`std::shared_ptr<T>()`に相当

		Returns:
			インスタンス
		"""
		return CSP(None)

	@classmethod
	def new(cls, origin: T_New) -> 'CSP[T_New]':
		"""メモリを生成し、共有ポインター型を返却するメモリ生成代替メソッド。C++では`std::make_shared`に相当

		Args:
			origin: 実体のインタンス
		Returns:
			インスタンス
		"""
		return CSP(CP(origin))

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

	def copy_proxy(self, via: 'CRef[T_co]') -> None:
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


class CWP(CVar[T_co]):
	"""C++型変数の互換クラス(弱参照ポインター)"""

	_weak: ReferenceType[T_co]

	def __init__(self, addr: CP[T_co]) -> None:
		"""インスタンスを生成

		Args:
			addr: ポインター
		"""
		self._weak = ReferenceType(addr.raw)
		self._hash = id(addr.raw)

	@property
	@override
	def on(self) -> T_co:
		"""Returns: 実体を返却 Note: リレー代替メソッド。C++では実体型は`.`、アドレス型は`->`に相当"""
		origin = self._weak()
		assert origin is not None, 'Origin is Null'
		return origin

	@property
	@override
	def raw(self) -> T_co | None:
		"""Returns: 実体を返却 Note: 実体参照代替メソッド。C++では実体型は削除、アドレス型は`*`に相当"""
		return self._weak()

	@property
	@override
	def _origin_raw(self) -> T_co | None:
		"""Returns: 実体を返却 Note: 派生クラス用。C++としての役割は無い"""
		return self._weak()

	def __hash__(self) -> int:
		"""ハッシュ値を取得

		Returns:
			ハッシュ値
		"""
		return self._hash


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


class CPConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(不変性ポインター)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: 不変性参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)


class CSPConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(不変性共有ポインター)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: 不変性参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: 不変性ポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRefConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(不変性参照)"""

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: 不変性ポインターを返却する参照変換代替メソッド。C++では`get`に相当"""
		return CPConst(self.raw)


class CRawConst(CVarNotNull[T_co]):
	"""C++型変数の互換クラス(不変性)"""

	@property
	def ref(self) -> 'CRefConst[T_co]':
		"""Returns: 不変性参照を返却する参照変換代替メソッド。C++では`*`に相当"""
		return CRefConst(self.raw)

	@property
	def addr(self) -> 'CPConst[T_co]':
		"""Returns: 不変性ポインターを返却する参照変換代替メソッド。C++では`&`に相当"""
		return CPConst(self.raw)
