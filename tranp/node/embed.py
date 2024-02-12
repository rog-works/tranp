from types import FunctionType
from typing import Any, Callable, NamedTuple, TypeVar, TypeAlias, cast

T_Data = TypeVar('T_Data')
MetaFactory: TypeAlias = Callable[[], dict[str, Any]]


class EmbedKeys(NamedTuple):
	"""埋め込みキー一覧"""

	AcceptTags = 'accept_tags'
	Actualized = 'actualized'
	Expandable = 'expandable'


class MetaData:
	"""メタデータコンテナー"""

	key = f'__meta_data_{id(__name__)}__'

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__classes: dict[type, dict[str, Any]] = {}
		self.__methods: dict[FunctionType, dict[str, Any]] = {}

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

	def set_for_class(self, ctor: type, embed_key: str, value: Any) -> None:
		"""メタデータを設定(クラス用)

		Args:
			ctor (type): 対象クラス
			embed_key (str): メタデータのキー
			value (Any): メタデータの値
		"""
		if ctor not in self.__classes:
			self.__classes[ctor] = {}

		self.__classes[ctor][embed_key] = value

	def set_for_method(self, method: FunctionType, embed_key: str, value: Any) -> None:
		"""メタデータを設定(メソッド用)

		Args:
			method (FunctionType): 対象メソッド
			embed_key (str): メタデータのキー
			value (Any): メタデータの値
		"""
		if method not in self.__methods:
			self.__methods[method] = {}

		self.__methods[method][embed_key] = value

	def get_by_key_from_class(self, embed_key: str) -> dict[type, Any]:
		"""メタデータを取得(クラス用)

		Args:
			method (FunctionType): 対象メソッド
			embed_key (str): メタデータのキー
		Returns:
			dict[type, Any]: 対象クラスとメタデータのマップ
		"""
		return {
			ctor: meta[embed_key]
			for ctor, meta in self.__classes.items()
			if embed_key in meta
		}

	def get_from_class(self, ctor: type, embed_key: str) -> Any:
		"""メタデータを取得(クラス用)

		Args:
			ctor (type): 対象クラス
			embed_key (str): メタデータのキー
		Returns:
			Any: メタデータの値
		Note:
			メタデータが存在しない場合はNoneを返却
		"""
		if ctor not in self.__classes:
			return None

		if embed_key not in self.__classes[ctor]:
			return None

		return self.__classes[ctor][embed_key]

	def get_from_method(self, ctor: type, embed_key: str) -> dict[str, Any]:
		"""メタデータを取得(メソッド用)

		Args:
			ctor (type): 対象クラス
			embed_key (str): メタデータのキー
		Returns:
			dict[str, Any]: 対象メソッドの名前とメタデータの値のマップ
		"""
		class_path = self.class_path(ctor)
		class_in_meta = {
			self.method_path(method): meta
			for method, meta in self.__methods.items()
			if self.method_path(method).startswith(f'{class_path}.')
		}
		return {
			in_path.split('.')[-1]: meta[embed_key]
			for in_path, meta in class_in_meta.items()
			if embed_key in meta
		}


class Meta:
	@classmethod
	def embed(cls, holder: type, *factories: MetaFactory) -> Callable:
		"""引数のクラスにメタデータを埋め込む
		ラップ対象のオブジェクトに関しては何も手を加えずそのまま返却
		埋め込み関数はメタデータを連想配列として返却する関数であれば何でも良い

		Args:
			holder (type): メタデータを保持するクラス
			*factories (MetaFactory): 埋め込み関数のリスト
		Returns:
			Callable: デコレーター
		Examples:
			```python
			@Meta.embed(MetaHolder, lambda: {'__embed_class_key__': 1})
			class A:
				@Meta.embed(MetaHolder, lambda: {'__embed_func_key__': 2})
				def func(self) -> None:
					...
			```
		"""
		def decorator(wrapped: type | FunctionType) -> type | FunctionType:
			for factory in factories:
				for embed_key, value in factory().items():
					if not hasattr(holder, MetaData.key):
						setattr(holder, MetaData.key, MetaData())

					meta_data = cast(MetaData, getattr(holder, MetaData.key))
					if type(wrapped) is FunctionType:
						# XXX 何故かFunctionTypeと見做されないのでcastで対処
						meta_data.set_for_method(cast(FunctionType, wrapped), embed_key, value)
					else:
						meta_data.set_for_class(wrapped, embed_key, value)

					setattr(holder, MetaData.key, meta_data)

			return wrapped

		return decorator

	@classmethod
	def dig_by_key_for_class(cls, holder, embed_key: str, value_type: type[T_Data]) -> dict[type, T_Data]:
		"""クラスに埋め込まれたメタデータを抽出(クラス用)

		Args:
			holder (type): メタデータを保持するクラス
			embed_key (str): 抽出対象の埋め込みキー
			value_type (type[T_Data]): メタデータの型
		Returns:
			dict[type, T_Data]: 対象クラスとメタデータのマップ
		"""
		if not hasattr(holder, MetaData.key):
			return {}

		meta_data = cast(MetaData, getattr(holder, MetaData.key))
		return meta_data.get_by_key_from_class(embed_key)

	@classmethod
	def dig_for_class(cls, holder: type, ctor: type, embed_key: str, default: T_Data) -> T_Data:
		"""クラスに埋め込まれたメタデータを抽出(クラス用)

		Args:
			holder (type): メタデータを保持するクラス
			ctor (type): 抽出対象のクラス
			embed_key (str): 抽出対象の埋め込みキー
			default (T_Data): メタデータが存在しない場合の返却値
		Returns:
			T_Data: メタデータ
		"""
		if not hasattr(holder, MetaData.key):
			return default

		meta_data = cast(MetaData, getattr(holder, MetaData.key))
		return meta_data.get_from_class(ctor, embed_key) or default

	@classmethod
	def dig_for_method(cls, holder: type, ctor: type, embed_key: str, value_type: type[T_Data]) -> dict[str, T_Data]:
		"""クラスに埋め込まれたメタデータを抽出(メソッド用)

		Args:
			holder (type): メタデータを保持するクラス
			ctor (type): 抽出対象のクラス
			embed_key (str): 抽出対象の埋め込みキー
			value_type (type[T_Data]): メタデータの型
		Returns:
			dict[str, T_Data]: メソッド毎のメタデータ
		"""
		if not hasattr(holder, MetaData.key):
			return {}

		meta_data = cast(MetaData, getattr(holder, MetaData.key))
		return meta_data.get_from_method(ctor, embed_key)


def accept_tags(*tags: str) -> MetaFactory:
	"""ノードに受け入れ対象のタグを埋め込む(クラス用)

	Args:
		*tags (str): 受け入れ対象のタグリスト
	Returns:
		MetaFactory: 埋め込み関数
	Note:
		派生クラスの定義は基底クラスの定義を上書きする
	Examples:
		```python
		@Meta.embed(Node, accept_tags('class'))
		class Class:
			...
		```
	"""
	return lambda: {EmbedKeys.AcceptTags: list(tags)}


def actualized(via: type) -> MetaFactory:
	"""引数の基底クラスからノード生成時に最適化対象としての情報を埋め込む(クラス用)

	Args:
		via (type): 基底クラス
	Returns:
		MetaFactory: 埋め込み関数
	Examples:
		```python
		class Base:
			...

		@Meta.embed(Node, actualized(via=Base))
		class Sub(Base):
			...
		```
	"""
	return lambda: {EmbedKeys.Actualized: via}


def expandable() -> dict[str, Any]:
	"""ノードのプロパティーを展開対象として情報を埋め込む(メソッド用)

	Returns:
		dict[str, Any]: メタデータ
	Note:
		展開される順序はメソッドの定義順に倣う
	Examples:
		```python
		class NodeA(Node):
			@property
			@embed_meta(Node, expandable)
			def prop_order0(self) -> int:
				...

			@property
			@embed_meta(Node, expandable)
			def prop_order1(self) -> int:
				...
		```
	"""
	return {EmbedKeys.Expandable: True}
