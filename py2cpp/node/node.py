from typing import TypeVar, cast

from py2cpp.ast.travarsal import EntryPath
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.annotation import implements
from py2cpp.lang.sequence import flatten
from py2cpp.node.base import NodeBase
from py2cpp.node.embed import EmbedKeys, Meta
from py2cpp.node.provider import Query
from py2cpp.node.trait import ScopeTrait


T = TypeVar('T', bound=NodeBase)
T_A = TypeVar('T_A', bound=NodeBase)
T_B = TypeVar('T_B', bound=NodeBase)


class Node(NodeBase):
	"""ASTのエントリーと紐づくノードの基底クラス
	自身のエントリーを基点にJSONPathクエリーベースで各ノードへ参照が可能
	派生クラスではノードの役割をプロパティーとして定義する

	Note:
		ASTを役割に適した形に単純化するため、AST上の余分な階層構造は排除する
		そのため、必ずしもAST上のエントリーとノードのアライメントは一致しない点に注意
	"""

	def __init__(self, nodes: Query['Node'], full_path: str) -> None:
		"""インスタンスを生成

		Args:
			nodes (Query[Node]): クエリーインターフェイス
			full_path (str): ルート要素からのフルパス
		"""
		self.__nodes = nodes
		self._full_path = EntryPath(full_path)


	@property
	@implements
	def full_path(self) -> str:
		"""str: ルート要素からのフルパス"""
		return self._full_path.origin


	@property
	def tag(self) -> str:
		"""str: エントリータグ名。具象クラスとのマッピングに用いる"""
		return self._full_path.last()[0]


	@property
	def scope_name(self) -> str:
		"""str: スコープ名を返却。@note: 名前空間を持たないノード以外は空文字"""
		return ''


	@property
	def namespace(self) -> str:  # FIXME 名前よりノードの方が良い。その場合名前をどう取得するかが課題
		"""str: 自身が所属する名前空間。@note: 所有する名前空間ではない点に注意"""
		if isinstance(self, ScopeTrait) and self.parent.scope_name:
			return f'{self.parent.namespace}.{self.parent.scope_name}'
		else:
			return self.parent.namespace


	@property
	def scope(self) -> str:  # FIXME 名前よりノードの方が良い。その場合名前をどう取得するかが課題
		"""str: 自身が所属するスコープ。@note: 所有するスコープではない点に注意"""
		if isinstance(self, ScopeTrait):
			return f'{self.parent.scope}.{self.parent.tag}'
		else:
			return self.parent.scope


	@property
	def nest(self) -> int:
		"""int: ネストレベル。スコープと同期"""
		return len(self.scope.split('.')) - 1


	@property
	def parent(self) -> 'Node':
		"""Node: 親のノード。@note: あくまでもノード上の親であり、AST上の親と必ずしも一致しない点に注意"""
		return self.__nodes.parent(self.full_path)


	@property
	def is_terminal(self) -> bool:
		"""bool: 終端要素。これ以上展開が不要な要素であることを表す。@note: 終端記号とは別"""
		return False


	def to_string(self) -> str:
		"""自身を表す文字列表現を取得

		Returns:
			str: 文字列表現
		"""
		return ''.join([self._my_value(), *[node.to_string() for node in self.flatten()]])


	def flatten(self) -> list['Node']:
		"""下位のノードを再帰的に展開し、1次元に平坦化して取得

		Returns:
			list[Node]: ノードリスト
		Note:
			# 優先順位
				1. 終端要素は空を返す
				2. 展開プロパティーのノードを使う
				3. 下位ノードを使う
			# 使い分け
				* 終端記号に紐づくノードが欲しい場合は_under_expansionを使う
				* 下位のノードを全て洗い出す場合はflattenを使う
		"""
		if self.is_terminal:
			return []

		under = self.__prop_expantion() or self._under_expansion()
		return list(flatten([[node, *node.flatten()] for node in under]))


	def __prop_expantion(self) -> list['Node']:
		"""展開プロパティーからノードリストを取得

		Returns:
			list[Node]: 展開プロパティーのノードリスト
		"""
		nodes: list[Node] = []
		for key in self.__expantionable_keys():
			func_or_result = getattr(self, key)
			result = cast(Node | list[Node], func_or_result() if callable(func_or_result) else func_or_result)
			nodes.extend(result if type(result) is list else [cast(Node, result)])

		return nodes


	def __expantionable_keys(self) -> list[str]:
		"""メタデータより展開プロパティーのメソッド名を抽出

		Returns:
			list[str]: 展開プロパティーのメソッド名リスト
		Note:
			@see trans.node.embed.expansionable
		"""
		prop_keys: dict[str, bool] = {}
		for ctor in self.__embed_classes():
			meta = Meta.dig_for_method(Node, ctor, EmbedKeys.Expansionable, value_type=int)
			order_on_keys = {value: name for name, value in meta.items()}
			prop_keys = {**prop_keys, **{prop_key: True for _, prop_key in sorted(order_on_keys.items(), key=lambda index: index)}}

		return list(prop_keys.keys())


	def __embed_classes(self) -> list[type['Node']]:
		"""自身を含む継承関係のあるクラスを取得。取得されるクラスはメタデータと関連する派生クラスに限定

		Returns:
			list[type[Node]]: クラスリスト
		Note:
			Node以下の基底クラスはメタデータと関わりがないため除外
		"""
		return [ctor for ctor in self.__class__.__mro__ if issubclass(ctor, Node) and ctor is not Node]


	def _exists(self, relative_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			relative_path (str): 自身のエントリーからの相対パス
		Returns:
			bool: True = 存在
		"""
		return self.__nodes.exists(self._full_path.joined(relative_path))


	def _by(self, relative_path: str) -> 'Node':
		"""指定のパスに紐づく一意なノードをフェッチ

		Args:
			relative_path (str): 自身のエントリーからの相対パス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: ノードが存在しない
		"""
		return self.__nodes.by(self._full_path.joined(relative_path))


	def _at(self, index: int) -> 'Node':
		"""指定のインデックスの子ノードをフェッチ

		Args:
			index (int): 子のインデックス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: ノードが存在しない
		"""
		children = self._children()
		if index < 0 or len(children) <= index:
			raise NotFoundError(self, index)

		return children[index]


	def _siblings(self, relative_path: str = '') -> list['Node']:
		"""指定のパスを基準に同階層のノードをフェッチ
		パスを省略した場合は自身と同階層を検索し、自身を除いたノードを返却

		Args:
			relative_path (str): 自身のエントリーからの相対パス(default = '')
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		via = self._full_path.joined(relative_path) if relative_path else self.full_path
		return [node for node in self.__nodes.siblings(via) if node.full_path != self.full_path]


	def _children(self, relative_path: str = '') -> list['Node']:
		"""指定のパスを基準に1階層下のノードをフェッチ
		パスを省略した場合は自身と同階層より1階層下を検索

		Args:
			relative_path (str): 自身のエントリーからの相対パス(default = '')
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		via = self._full_path.joined(relative_path) if relative_path else self.full_path
		return self.__nodes.children(via)


	def _leafs(self, leaf_tag: str) -> list['Node']:
		"""配下に存在する接尾辞が一致するノードをフェッチ

		Args:
			leaf_name (str): 接尾辞
		Returns:
			list[Node]: ノードリスト
		"""
		return self.__nodes.leafs(self.full_path, leaf_tag)


	def _under_expansion(self) -> list['Node']:
		"""配下に存在する展開が可能なノードをフェッチ

		Returns:
			list[Node]: ノードリスト
		"""
		return self.__nodes.expansion(self.full_path)


	def _my_value(self) -> str:
		"""自身のエントリーの値を取得

		Returns:
			str: 値
		"""
		return self.__nodes.by_value(self.full_path)


	def as_a(self, ctor: type[T]) -> T:
		"""指定の具象クラスに変換。変換先が同種(同じか派生クラス)の場合はキャストするのみ

		Args:
			ctor (type[T]): 具象クラスの型
		Returns:
			T: 具象クラスのインスタンス
		Raises:
			LogicError: 許可されない変換先を指定
		Note:
			XXX 変換先は継承関係が無くても良い
		"""
		if self.is_a(ctor):
			return cast(T, self)

		accept_tags = self.__accept_tags()
		if len(accept_tags) and self.tag not in accept_tags:
			raise LogicError(str(self), ctor)

		return ctor(self.__nodes, self.full_path)


	def __accept_tags(self) -> list[str]:
		"""メタデータより受け入れタグリストを取得

		Returns:
			list[str]: 受け入れタグリスト
		"""
		accept_tags: dict[str, bool] = {}
		for ctor in self.__embed_classes():
			accept_tags = {**accept_tags, **{in_tag: True for in_tag in Meta.dig_for_class(Node, ctor, EmbedKeys.AcceptTags, default=[])}}

		return list(accept_tags.keys())


	def is_a(self, ctor: type[NodeBase]) -> bool:
		"""指定のクラスと同種(同じか派生クラス)のインスタンスか判定

		Args:
			ctor (type[NodeBase]): 判定するクラス
		Returns:
			bool: True = 同種
		"""
		return isinstance(self, ctor)


	def if_not_a_to_b(self, reject_type: type[T_A], expect_type: type[T_B]) -> T_A | T_B:
		"""AでなければBに変換

		Args:
			reject_type (type[T_A]): 除外する型
			expect_type (type[T_B]): 期待する型
		Returns:
			T1 | T2: AかBの型
		"""
		return cast(reject_type, self) if type(self) is reject_type else self.as_a(expect_type)


	@classmethod
	def match_feature(cls, via: 'Node') -> bool:
		"""引数のノードが自身の特徴と一致するか判定
		一致すると判断されたノードはactualizeにより変換される
		条件判定は派生クラス側で実装

		Args:
			via (Node): 変換前のノード
		Returns:
			bool: True = 一致
		Note:
			@see actualize, _features
		"""
		return False


	def _feature_classes(self) -> list[type['Node']]:
		"""メタデータより自身に紐づけられた特徴クラス(=派生クラス)を抽出

		Returns:
			list[type[Node]]: 特徴クラスのリスト
		"""
		classes: dict[type[Node], bool] = {}
		for ctor in self.__embed_classes():
			meta = Meta.dig_by_key_for_class(Node, EmbedKeys.Actualized, value_type=type)
			classes = {**classes, **{feature_class: True for feature_class, via_class in meta.items() if via_class is ctor}}

		return list(classes.keys())


	def actualize(self) -> 'Node':
		"""ASTの相関関係より判断した実体としてより適切な具象クラスのインスタンスに変換。条件は具象側で実装

		Returns:
			Node: 具象クラスのインスタンス
		"""
		for feature_class in self._feature_classes():
			if feature_class.match_feature(self):
				return self.as_a(feature_class)

		return self


	def __str__(self) -> str:
		"""str: 文字列表現を取得"""
		return f'<{self.__class__.__name__}: {self.full_path}>'


	# XXX def is_statement(self) -> bool: pass
	# XXX def pretty(self) -> str: pass
