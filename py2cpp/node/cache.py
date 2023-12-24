from typing import Any, Callable, Generic, ParamSpec, TypeVar

from py2cpp.node.base import NodeBase
from py2cpp.node.node import Node
from py2cpp.node.embed import EmbedKeys, Meta

T = TypeVar('T', bound=NodeBase)
T_Ret = TypeVar('T_Ret')
P = ParamSpec('P')


class Memoize:
	__memo: dict[Callable, Any] = {}

	@classmethod
	def memo(cls, wrapped: Callable[P, T_Ret]) -> Callable[P, T_Ret]:
		def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_Ret:
			if wrapped.__name__ not in cls.__memo:
				cls.__memo[wrapped] = wrapped(*args, **kwargs)

			return cls.__memo[wrapped]

		return wrapper


class MetaCache(Generic[T]):
	def __init__(self, holder: type[T], ctor: type[T]) -> None:
		self.__holder = holder
		self.__ctor = ctor

	def has(self, ctor: type[T]) -> bool:
		return ctor == self.__ctor

	@Memoize.memo
	def expands(self) -> list[str]:
		prop_keys: list[str] = []
		for ctor in self.__embed_classes():
			meta = Meta.dig_for_method(self.__holder, ctor, EmbedKeys.Expandable, value_type=bool)
			prop_keys = [*prop_keys, *[name for name, _ in meta.items()]]

		return prop_keys

	@Memoize.memo
	def actualized(self) -> list[type[T]]:
		classes: dict[type[T], bool] = {}
		for ctor in self.__embed_classes():
			meta = Meta.dig_by_key_for_class(self.__holder, EmbedKeys.Actualized, value_type=type)
			classes = {**classes, **{feature_class: True for feature_class, via_class in meta.items() if via_class is ctor}}

		return list(classes.keys())

	@Memoize.memo
	def accept_tags(self) -> list[str]:
		accept_tags: dict[str, bool] = {}
		for ctor in self.__embed_classes():
			accept_tags = {**accept_tags, **{in_tag: True for in_tag in Meta.dig_for_class(Node, ctor, EmbedKeys.AcceptTags, default=[])}}

		return list(accept_tags.keys())

	def __embed_classes(self) -> list[type['Node']]:
		"""対象のクラス自身を含む継承関係のあるクラスを基底クラス順に取得。取得されるクラスはメタデータと関連する派生クラスに限定

		Args:
			via (type[NodeBase]): 対象のクラス
		Returns:
			list[type[Node]]: クラスリスト
		Note:
			Node以下の基底クラスはメタデータと関わりがないため除外
		"""
		classes = [ctor for ctor in self.__ctor.__mro__ if issubclass(ctor, Node) and ctor is not Node]
		return list(reversed(classes))
