from types import FunctionType
from typing import Any, Callable, cast, NamedTuple, TypeVar, TypeAlias

T_Wrapped = TypeVar('T_Wrapped', type, FunctionType)
MetaFactory: TypeAlias = Callable[[], dict[str, Any]]
EmbedMeta: TypeAlias = dict[str, dict[str, Any]]


class EmbedKeys(NamedTuple):
	"""埋め込みキー一覧"""

	Expansionable = 'expansionable'


class MetaData:
	"""メタデータコンテナー"""

	@classmethod
	@property
	def key(cls) -> str:
		"""str: 保持クラスに追加するメタデータのプロパティ名"""
		return f'__meta_data_{cls.__hash__}__'


	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__classes: EmbedMeta = {}
		self.__methods: EmbedMeta = {}


	def class_path(self, ctor: type) -> str:
		"""クラスのモジュールパスを取得

		Args:
			ctor (type): クラス
		Returns:
			str: モジュールパス
		"""
		return f'{ctor.__module__}.{ctor.__name__}'


	def method_path(self, method: FunctionType) -> str:
		"""メソッドのモジュールパスを取得

		Args:
			method (FunctionType): メソッド
		Returns:
			str: モジュールパス
		"""
		return f'{method.__module__}.{method.__qualname__.split(".")[-2]}.{method.__name__}'


	def for_class(self, ctor: type, embed_key: str, value: Any) -> None:
		"""メタデータを設定(クラス用)

		Args:
			ctor (type): 対象クラス
			embed_key (str): メタデータのキー
			value (Any): メタデータの値
		"""
		path = self.class_path(ctor)
		if path not in self.__classes:
			self.__classes[path] = {}

		self.__classes[path][embed_key] = value


	def for_method(self, method: FunctionType, embed_key: str, value: Any) -> None:
		"""メタデータを設定(メソッド用)

		Args:
			method (FunctionType): 対象メソッド
			embed_key (str): メタデータのキー
			value (Any): メタデータの値
		"""
		path = self.method_path(method)
		if path not in self.__methods:
			self.__methods[path] = {}

		self.__methods[path][embed_key] = value


	def fetch_from_class(self, ctor: type, embed_key: str) -> Any:
		"""メタデータを取得(クラス用)

		Args:
			method (FunctionType): 対象メソッド
			embed_key (str): メタデータのキー
		Returns:
			Any: メタデータの値
		"""
		class_path = self.class_path(ctor)
		return self.__classes[class_path][embed_key]


	def fetch_from_method(self, ctor: type, embed_key: str) -> dict[str, Any]:
		"""メタデータを取得(メソッド用)

		Args:
			method (FunctionType): 対象メソッド
			embed_key (str): メタデータのキー
		Returns:
			Any: メタデータの値
		"""
		class_path = self.class_path(ctor)
		class_in_meta = {in_path: meta for in_path, meta in self.__methods.items() if in_path.startswith(f'{class_path}.')}
		return {
			in_path.split('.')[-1]: meta[embed_key]
			for in_path, meta in class_in_meta.items()
			if embed_key in meta
		}


def embed_meta(holder: type, *factories: MetaFactory) -> Callable:
	"""引数のクラスにメタデータを埋め込む
	ラップ対象のオブジェクトに関しては何も手を加えずそのまま返却
	埋め込み関数はメタデータを連想配列として返却する関数であれば何でも良い

	Args:
		holder (type): メタデータを保持するクラス
		*factories (MetaFactory): 埋め込み関数のリスト
	Returns:
		Callable: デコレーター
	Usage:
		```python
		@embed_meta(MetaHolder, lambda: {'__embed_class_key__': 1})
		class A:
			@embed_meta(MetaHolder, lambda: {'__embed_func_key__': 2})
			def func(self) -> None:
				...
		```
	"""
	def decorator(wrapped: T_Wrapped) -> T_Wrapped:
		for factory in factories:
			for embed_key, value in factory().items():
				if not hasattr(holder, MetaData.key):
					setattr(holder, MetaData.key, MetaData())

				meta_data = cast(MetaData, getattr(holder, MetaData.key))
				if type(wrapped) is FunctionType:
					meta_data.for_method(wrapped, embed_key, value)
				else:
					meta_data.for_class(wrapped, embed_key, value)

				setattr(holder, MetaData.key, meta_data)

		return wrapped

	return decorator


def digging_meta_class(holder: type, ctor: type, embed_key: str) -> Any:
	"""クラスに埋め込まれたメタデータを抽出(クラス用)

	Args:
		holder (type): メタデータを保持するクラス
		ctor (type): 抽出対象のクラス
		embed_key (str): 抽出対象の埋め込みキー
	Returns:
		Any: メタデータ
	"""
	if not hasattr(holder, MetaData.key):
		raise ValueError()

	meta_data = cast(MetaData, getattr(holder, MetaData.key))
	return meta_data.fetch_from_class(ctor, embed_key)


def digging_meta_method(holder: type, ctor: type, embed_key: str) -> dict[str, Any]:
	"""クラスに埋め込まれたメタデータを抽出(メソッド用)

	Args:
		holder (type): メタデータを保持するクラス
		ctor (type): 抽出対象のクラス
		embed_key (str): 抽出対象の埋め込みキー
	Returns:
		dict[str, Any]: メソッド毎のメタデータ
	"""
	if not hasattr(holder, MetaData.key):
		raise ValueError()

	meta_data = cast(MetaData, getattr(holder, MetaData.key))
	return meta_data.fetch_from_method(ctor, embed_key)


def expansionable(order: int) -> MetaFactory:
	"""ノードにプロパティーとしてのタグと評価順序を埋め込む

	Args:
		order (int): プロパティーの評価順序
	Returns:
		MetaFactory: 埋め込み関数
	Usage:
		class A:
			@property
			@embed_meta(Node, expansionable(order=0))
			def prop_order0(self) -> int:
				...

			@property
			@embed_meta(Node, expansionable(order=1))
			def prop_order1(self) -> int:
				...
	"""
	return lambda: {EmbedKeys.Expansionable: order}
