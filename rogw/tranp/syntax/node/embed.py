from collections.abc import Callable
from types import FunctionType
from typing import Any, NamedTuple, TypeVar, TypeAlias, cast

T_Data = TypeVar('T_Data')
MetaFactory: TypeAlias = Callable[[], dict[str, Any]]


class EmbedKeys(NamedTuple):
	"""埋め込みキー一覧"""

	AcceptTags = 'accept_tags'
	Expandable = 'expandable'


class MetaData:
	"""メタデータコンテナー"""

	key = f'__meta_data_{id(__name__)}__'

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__classes: dict[type, dict[str, Any]] = {}
		self.__methods: dict[str, dict[str, dict[str, Any]]] = {}

	def class_path(self, ctor: type) -> str:
		"""クラスのモジュールパスを取得

		Args:
			ctor: クラス
		Returns:
			モジュールパス
		"""
		return f'{ctor.__module__}.{ctor.__name__}'

	def method_path(self, method: FunctionType) -> str:
		"""メソッドのモジュールパスを取得

		Args:
			method: メソッド
		Returns:
			モジュールパス
		"""
		class_name = method.__qualname__.split('.')[-2]
		return f'{method.__module__}.{class_name}.{method.__name__}'

	def set_for_class(self, ctor: type, embed_key: str, value: Any) -> None:
		"""メタデータを設定(クラス用)

		Args:
			ctor: 対象クラス
			embed_key: メタデータのキー
			value: メタデータの値
		"""
		if ctor not in self.__classes:
			self.__classes[ctor] = {}

		self.__classes[ctor][embed_key] = value

	def set_for_method(self, method: FunctionType, embed_key: str, value: Any) -> None:
		"""メタデータを設定(メソッド用)

		Args:
			method: 対象メソッド
			embed_key: メタデータのキー
			value: メタデータの値
		"""
		elems = self.method_path(method).split('.')
		method_name = elems.pop()
		class_path = '.'.join(elems)
		if class_path not in self.__methods:
			self.__methods[class_path] = {}

		if method_name not in self.__methods[class_path]:
			self.__methods[class_path][method_name] = {}

		self.__methods[class_path][method_name][embed_key] = value

	def get_from_class(self, ctor: type, embed_key: str) -> Any:
		"""メタデータを取得(クラス用)

		Args:
			ctor: 対象クラス
			embed_key: メタデータのキー
		Returns:
			メタデータの値
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
			ctor: 対象クラス
			embed_key: メタデータのキー
		Returns:
			対象メソッドの名前とメタデータの値のマップ
		"""
		class_path = self.class_path(ctor)
		class_in_meta = self.__methods.get(class_path, {})
		return {method_name: meta[embed_key] for method_name, meta in class_in_meta.items() if embed_key in meta}


class Meta:
	@classmethod
	def embed(cls, holder: type, *factories: MetaFactory) -> Callable:
		"""引数のクラスにメタデータを埋め込む
		ラップ対象のオブジェクトに関しては何も手を加えずそのまま返却
		埋め込み関数はメタデータを連想配列として返却する関数であれば何でも良い

		Args:
			holder: メタデータを保持するクラス
			*factories: 埋め込み関数のリスト
		Returns:
			デコレーター
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
	def dig_for_class(cls, holder: type, ctor: type, embed_key: str, default: T_Data) -> T_Data:
		"""クラスに埋め込まれたメタデータを抽出(クラス用)

		Args:
			holder: メタデータを保持するクラス
			ctor: 抽出対象のクラス
			embed_key: 抽出対象の埋め込みキー
			default: メタデータが存在しない場合の返却値
		Returns:
			メタデータ
		"""
		if not hasattr(holder, MetaData.key):
			return default

		meta_data = cast(MetaData, getattr(holder, MetaData.key))
		return meta_data.get_from_class(ctor, embed_key) or default

	@classmethod
	def dig_for_method(cls, holder: type, ctor: type, embed_key: str, value_type: type[T_Data]) -> dict[str, T_Data]:
		"""クラスに埋め込まれたメタデータを抽出(メソッド用)

		Args:
			holder: メタデータを保持するクラス
			ctor: 抽出対象のクラス
			embed_key: 抽出対象の埋め込みキー
			value_type: メタデータの型
		Returns:
			メソッド毎のメタデータ
		"""
		if not hasattr(holder, MetaData.key):
			return {}

		meta_data = cast(MetaData, getattr(holder, MetaData.key))
		return meta_data.get_from_method(ctor, embed_key)


def accept_tags(*tags: str) -> MetaFactory:
	"""ノードに受け入れ対象のタグを埋め込む(クラス用)

	Args:
		*tags: 受け入れ対象のタグリスト
	Returns:
		埋め込み関数
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


def expandable() -> dict[str, Any]:
	"""ノードのプロパティーを展開対象として情報を埋め込む(メソッド用)

	Returns:
		メタデータ
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
