from typing import Any, Callable, NamedTuple, TypeVar, TypeAlias

T_Embeded = TypeVar('T_Embeded', type, Callable)

Embedder: TypeAlias = Callable[[], dict[str, Any]]


class EmbedKeys(NamedTuple):
	NodeProp = '__node_prop__'


def embed_meta(*embedders: Embedder) -> Callable:
	"""クラス・関数・メソッドにメタ情報を埋め込む。実体は変えずにそのまま返却
	埋め込み関数はメタデータを連想配列として返却する関数であれば何でも良い

	Args:
		*embedders (Embedder): 埋め込み関数のリスト
	Returns:
		Callable: デコレーター
	Note:
		埋め込み先に寄らず、他のデコレーターと共存させるのは基本的にNG
		特に@propertyデコレーターと相性が悪いため、その場合は共存不可
		それでも共存させる場合は、埋め込んだオブジェクトが隠されるの避けるため、最も外側で実行すること
	Usage:
		```python
		@embed_meta(lambda: {'__embed_class_key__': 1})
		class A:
			@embed_meta(lambda: {'__embed_func_key__': 2})
			def func(self) -> None:
				...
		```
	"""
	def decorator(embeded: T_Embeded) -> T_Embeded:
		for embedder in embedders:
			for embed_key, value in embedder().items():
				if hasattr(embeded, embed_key):
					raise ValueError()

				setattr(embeded, embed_key, value)

		return embeded

	return decorator


def node_properties(*props: str) -> Embedder:
	"""ノードにプロパティーとしてのタグと評価順序を埋め込む

	Args:
		*props (str): 評価順で並べたプロパティー名リスト
	Returns:
		Embedder: 埋め込み関数
	Note:
		埋め込み先はクラスになるため、埋め込みキーの末尾にプロパティー名が付与される
		例) '__embed_key__' -> '__embed_key__.${method_name}'
	Usage:
		@embed_meta(node_properties('prop_order0', 'prop_order1'))
		class A:
			@property
			def prop_order0(self) -> int:
				...

			@property
			def prop_order1(self) -> int:
				...
	"""
	return lambda: {f'{EmbedKeys.NodeProp}.{prop_name}': order for order, prop_name in enumerate(props)}
