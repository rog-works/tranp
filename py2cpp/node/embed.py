from types import FunctionType
from typing import Any, Callable, NamedTuple, TypeVar, TypeAlias

T_Wrapped = TypeVar('T_Wrapped', type, FunctionType)
MetaFactory: TypeAlias = Callable[[], dict[str, Any]]
EmbedMeta: TypeAlias = dict[str, dict[str, Any]]


class EmbedKeys(NamedTuple):
	"""埋め込みキー一覧"""

	Expansionable = '__embed_meta_expansionable__'


def embed_meta(holder: type, *factories: MetaFactory) -> Callable:
	"""引数のクラスにメタ情報を埋め込む
	ラップ対象のオブジェクトに関しては何も手を加えずそのまま返却
	埋め込み関数はメタデータを連想配列として返却する関数であれば何でも良い

	Args:
		holder (type): メタ情報を保持するクラス
		*factories (MetaFactory): 埋め込み関数のリスト
	Returns:
		Callable: デコレーター
	Raises:
		ValueError: キー名の重複
	Note:
		# 保存時の埋め込みキーの書式
			クラスに情報を埋め込むため、埋め込みキーの末尾にクラスのモジュールパスとメソッド名が付与される
			例) '__embed_key__' -> '__embed_key__:${$method.__module__}.${method.__class__.__name__}:${method.__name__}'
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
			for in_embed_key, value in factory().items():
				embed_key = __build_embed_key(wrapped, in_embed_key)
				if hasattr(holder, embed_key):
					raise ValueError()

				setattr(holder, embed_key, value)

		return wrapped

	return decorator


def __build_embed_key(wrapped: T_Wrapped, embed_key: str) -> str:
	"""参照情報を付与した埋め込みキーを生成

	Args:
		wrapped (T_Wrapped): デコレーターのラップ対象
		embed_key (str): 埋め込みキー
	Returns:
		str: 生成した埋め込みキー
	"""
	if type(wrapped) is FunctionType:
		return f'{embed_key}:{wrapped.__module__}.{wrapped.__qualname__.split(".")[-2]}:{wrapped.__name__}'
	else:
		return f'{embed_key}:{wrapped.__module__}.{wrapped.__name__}'


def expansionable(order: int) -> MetaFactory:
	"""ノードにプロパティーとしてのタグと評価順序を埋め込む

	Args:
		order (int): プロパティーの評価順序
	Returns:
		Embedder: 埋め込み関数
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


def digging_meta(holder: type) -> tuple[EmbedMeta, EmbedMeta]:
	"""クラスに埋め込まれたメタ情報を抽出

	Args:
		holder (type): メタ情報を保持するクラス
	Returns:
		tuple[EmbedMeta, EmbedMeta]: (クラスのメタ情報, メソッドのメタ情報)
	"""
	flat_meta = {key: value for key, value in holder.__dict__.items() if key.startswith('__embed_meta')}
	meta_class: EmbedMeta = {}
	meta_method: EmbedMeta = {}
	for key, value in flat_meta.items():
		embed_key, class_module_path, method_name = key.split(':')
		if method_name:
			full_name = f'{class_module_path}:{method_name}'
			if full_name not in meta_method:
				meta_method[full_name] = {}

			meta_method[full_name][embed_key] = value
		else:
			meta_class[class_module_path][embed_key] = value

	return meta_class, meta_method


def digging_meta_method(holder: type, ctor: type, embed_key: str) -> EmbedMeta:
	"""クラスに埋め込まれたメタ情報を抽出(メソッド用)

	Args:
		holder (type): メタ情報を保持するクラス
		ctor (type): 抽出対象のクラス
		embed_key (str): 抽出対象の埋め込みキー
	Returns:
		EmbedMeta: メソッドのメタ情報
	"""
	_, meta_method = digging_meta(holder)
	filtered_meta = {name: in_meta[embed_key] for name, in_meta in meta_method.items() if embed_key in in_meta}
	return {
		full_name.split(':')[-1]: value
		for full_name, value in filtered_meta.items()
		 if full_name.startswith(f'{ctor.__module__}.{ctor.__name__}:')
	}
