import functools
from typing import Iterator, TypeVar, cast

from py2cpp.ast.travarsal import EntryPath
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.annotation import implements
from py2cpp.lang.sequence import flatten
from py2cpp.lang.string import snakelize
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
		"""str: エントリータグ。具象クラスとのマッピングに用いる。@note: あくまでもマッチパターンに対するタグであり、必ずしも共通の構造を表さない点に注意"""
		return self._full_path.last()[0]

	@property
	def identifer(self) -> str:
		"""str: 構造に対する識別子。実質的に派生クラスに対する識別子"""
		return snakelize(self.__class__.__name__)

	@property
	def is_terminal(self) -> bool:
		"""bool: 終端要素。これ以上展開が不要な要素であることを表す。@note: 終端記号とは別"""
		return False

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
				* 終端記号に紐づくノードが欲しい場合は_under_expansion
				* 下位のノードを全て洗い出す場合はflatten
				* ASTの計算順序の並びで欲しい場合はcalculated
		"""
		if self.is_terminal:
			return []

		under = self.__prop_expantion() or self._under_expansion()
		return list(flatten([[node, *node.flatten()] for node in under]))

	def calculated(self) -> list['Node']:
		"""ASTの計算順序に合わせた順序で配下のノードを1次元に展開

		Returns:
			list[Node]: ノードリスト
		Note:
			flattenとの相違点は並び順のみ
		"""
		path_of_nodes = {node.full_path: node for node in self.flatten()}
		sorted_paths = self.__calclation_order(enumerate(path_of_nodes.keys()))
		return [path_of_nodes[full_path] for full_path in sorted_paths]

	def __calclation_order(self, index_of_paths: Iterator[tuple[int, str]]) -> list[str]:
		"""インデックスとフルパスを元にツリーの計算順序にソート

		Args:
			index_of_paths (Iterator[tuple[int, str]]): (インデックス, フルパス)形式のイテレーター
		Returns:
			list[str]: 並び替え後のパスリスト
		"""
		def order(a: tuple[int, str], b: tuple[int, str]) -> int:
			aindex, apath = a
			bindex, bpath = b
			if apath.startswith(bpath):
				return -1
			else:
				return -1 if aindex < bindex else 1

		return [path for _, path in sorted(index_of_paths, key=functools.cmp_to_key(order))]

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
		order_on_keys: dict[int, str] = {}
		for ctor in self.__embed_classes(self.__class__):
			meta = Meta.dig_for_method(Node, ctor, EmbedKeys.Expansionable, value_type=int)
			in_order_on_keys = {value: name for name, value in meta.items()}
			order_on_keys = {**order_on_keys, **in_order_on_keys}

		prop_keys = {prop_key: True for _, prop_key in sorted(order_on_keys.items(), key=lambda index: index)}
		return list(prop_keys.keys())

	def __embed_classes(self, via: type[NodeBase]) -> list[type['Node']]:
		"""対象のクラス自身を含む継承関係のあるクラスを基底クラス順に取得。取得されるクラスはメタデータと関連する派生クラスに限定

		Args:
			via (type[NodeBase]): 対象のクラス
		Returns:
			list[type[Node]]: クラスリスト
		Note:
			Node以下の基底クラスはメタデータと関わりがないため除外
		"""
		classes = [ctor for ctor in via.__mro__ if issubclass(ctor, Node) and ctor is not Node]
		return list(reversed(classes))

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

	def _at_child(self, index: int) -> 'Node':
		"""展開できる子ノードをフェッチ

		Args:
			index (int): 子のインデックス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: 子が存在しない
		Note:
			@deprecated
		"""
		under = self._under_expansion()
		if index < 0 or len(under) <= index:
			raise NotFoundError(str(self), index)

		return under[index]

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

	def as_a(self, to_class: type[T]) -> T:
		"""指定の具象クラスに変換。変換先が同種(同じか派生クラス)の場合はキャストするのみ

		Args:
			to_class (type[T]): 変換先の具象クラス
		Returns:
			T: 具象クラスのインスタンス
		Raises:
			LogicError: 許可されない変換先を指定
		Note:
			XXX 変換先は継承関係が無くても良い
			変換先の受け入れ範囲が広い場合(Expressionなど)、何でも変換できてしまうので注意
		"""
		if self.is_a(to_class):
			return cast(T, self)

		accept_tags = self.__accept_tags(to_class)
		if len(accept_tags) and self.tag not in accept_tags:
			raise LogicError(str(self), to_class)

		return to_class(self.__nodes, self.full_path)

	def __accept_tags(self, to_class: type[NodeBase]) -> list[str]:
		"""メタデータより変換先の受け入れタグリストを取得

		Args:
			to_class (type[NodeBase]): 変換先の具象クラス
		Returns:
			list[str]: 受け入れタグリスト
		"""
		accept_tags: dict[str, bool] = {}
		for ctor in self.__embed_classes(to_class):
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
			T1 | T2: AかB
		"""
		return cast(reject_type, self) if self.is_a(reject_type) else self.as_a(expect_type)

	def if_a_actualize_from_b(self, expect_type: type[T_A], through_type: type[T_B]) -> 'Node':
		"""AならBを介して適切な具象クラスに変換

		Args:
			expect_type (type[T_A]): 期待する型
			through_type (type[T_B]): 仲介する型
		Returns:
			Node: A以外か、Bから変換した具象クラス
		Note:
			変換先のクラスは状況次第のため不明
		"""
		return cast(Node, self.as_a(through_type)).actualize() if self.is_a(expect_type) else self

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
		for ctor in self.__embed_classes(self.__class__):
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
