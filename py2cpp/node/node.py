from typing import Callable, cast, Iterator, TypeVar

from lark import Token

from py2cpp.ast.travarsal import ASTFinder
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.sequence import flatten
from py2cpp.node.embed import digging_meta_class, digging_meta_method, EmbedKeys
from py2cpp.node.provider import Query
from py2cpp.node.trait import ScopeTrait
from py2cpp.tp_lark.types import Entry

T = TypeVar('T')
T_A = TypeVar('T_A')
T_B = TypeVar('T_B')


class Node:
	"""ASTのエントリーと紐づくノードの基底クラス
	自身を基点に各ノードへJSONPathライクに相対参照が可能
	派生クラスではノードの役割をプロパティーとして定義する

	Note:
		ASTを役割に適した形に単純化するため、AST上の余分な階層構造は排除する
		そのため、必ずしもAST上のエントリーとノードのアライメントは一致しない点に注意
	"""

	def __init__(self, nodes: Query['Node'], entry: Entry, full_path: str) -> None:
		"""インスタンスを生成

		Args:
			nodes (Query[Node]): クエリーインターフェイス
			entry (Entry): 自身のエントリー
			full_path (str): ルート要素からのフルパス
		"""
		self.__nodes = nodes
		self.__entry = entry
		self.__full_path = full_path


	@property
	def full_path(self) -> str:
		"""str: ルート要素からのフルパス"""
		return self.__full_path


	@property
	def tag(self) -> str:
		"""str: エントリータグ名。具象クラスとのマッピングに用いる"""
		return ASTFinder.denormalize_tag(self.full_path.split('.').pop())


	@property
	def token(self) -> str:
		"""自身に紐づくエントリーから終端記号を取得

		Returns:
			str: 終端記号
		Note:
			XXX エントリーがトークンではない場合、空文字を返す
		"""
		return self.__entry.value if type(self.__entry) is Token else ''


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
	def props(self) -> list['Node']:
		"""list[Node]: 自身が所有するノードをプロパティーリストとして取得。@note: AST上の子と必ずしも一致しない点に注意"""
		nodes: list[Node] = []
		for key in self.__node_prop_keys():
			func_or_result = cast(Callable, getattr(self, key))
			result = func_or_result() if callable(func_or_result) else func_or_result
			nodes.extend(result if type(result) is list else [result])

		return nodes


	def __node_prop_keys(self) -> list[str]:
		"""派生クラスでプロパティーとして定義されたメソッドの名前を抽出

		Returns:
			list[str]: プロパティーのメソッド名リスト
		Note:
			@see trans.node.embed.expansionable
		"""
		meta = digging_meta_method(Node, self.__class__, EmbedKeys.Expansionable)
		order_on_keys = {cast(int, value): name for name, value in meta.items()}
		return [prop_key for _, prop_key in sorted(order_on_keys.items(), key=lambda index: index)]


	def __iter__(self) -> Iterator['Node']:
		"""プロパティーのイテレーター

		Returns:
			Iterator[Node]: イテレーター
		"""
		for prop in self.props:
			yield prop


	def _to_full_path(self, relative_path: str) -> str:
		"""フルパスへ変換

		Args:
			relative_path (str): 自身のエントリーからの相対パス
		Returns:
			str: フルパス
		"""
		return f'{self.full_path}.{relative_path}'


	def _exists(self, relative_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			relative_path (str): 自身のエントリーからの相対パス
		Returns:
			bool: True = 存在
		"""
		return self.__nodes.exists(self._to_full_path(relative_path))


	def _by(self, relative_path: str) -> 'Node':
		"""指定のパスに紐づく一意なノードをフェッチ

		Args:
			relative_path (str): 自身のエントリーからの相対パス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: ノードが存在しない
		"""
		return self.__nodes.by(self._to_full_path(relative_path))


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
		via = self._to_full_path(relative_path) if relative_path else self.full_path
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
		via = self._to_full_path(relative_path) if relative_path else self.full_path
		return self.__nodes.children(via)


	def _leafs(self, leaf_tag: str) -> list['Node']:
		"""配下に存在する接尾辞が一致するノードをフェッチ

		Args:
			leaf_name (str): 接尾辞
		Returns:
			list[Node]: ノードリスト
		"""
		return self.__nodes.leafs(self.full_path, leaf_tag)


	def _expansion(self) -> list['Node']:
		"""配下に存在する展開が可能なノードをフェッチ

		Returns:
			list[Node]: ノードリスト
		"""
		return self.__nodes.expansion(self.full_path)


	def flatten(self) -> list['Node']:
		"""下位のノードを再帰的に展開し、1次元に平坦化して取得

		Returns:
			list[Node]: ノードリスト
		"""
		return list(flatten([[node, *node.flatten()] for node in self._expansion()]))


	def as_a(self, ctor: type[T]) -> T:
		"""指定の具象クラスに変換。変換先が同じ場合は何もしない

		Args:
			ctor (type[T]): 具象クラスの型
		Returns:
			T: 具象クラスのインスタンス
		Raises:
			LogicError: 許可されない変換先を指定
		"""
		if type(self) is ctor:
			return cast(T, self)

		accept_tags: list[str] = digging_meta_class(Node, ctor, EmbedKeys.AcceptTags, default=[])
		if len(accept_tags) and self.tag not in accept_tags:
			raise LogicError(str(self), ctor)

		return ctor(self.__nodes, self.__entry, self.__full_path)


	def is_a(self, ctor: type['Node']) -> bool:
		"""指定のクラスのインスタンスか判定

		Args:
			ctor (type[Node]): クラス
		Returns:
			bool: True = 同じ
		Note:
			完全一致を判定するため、サブクラスも偽である点に注意
		"""
		return type(self) is ctor


	def if_not_a_to_b(self, reject_type: type[T_A], expect_type: type[T_B]) -> T_A | T_B:
		"""AでなければBに変換

		Args:
			reject_type (type[T_A]): 除外する型
			expect_type (type[T_B]): 期待する型
		Returns:
			T1 | T2: AかBの型
		"""
		return cast(reject_type, self) if type(self) is reject_type else self.as_a(expect_type)


	def actual(self) -> 'Node':
		"""ASTの相関関係より判断した実体としてより適切な具象クラスのインスタンスに変換。具象側で実装

		Returns:
			Node: 具象クラスのインスタンス
		Note:
			基底クラスでは判断できないため、デフォルトでは自分自身を返却
		"""
		return self


	def __str__(self) -> str:
		"""str: 文字列表現を取得"""
		return f'<{self.__class__.__name__}: {self.full_path}>'


	# XXX def is_method(self) -> bool: pass
	# XXX def is_statement(self) -> bool: pass
	# XXX def is_terminal(self) -> bool: pass
	# XXX def is_token(self) -> bool: pass
	# XXX def pretty(self) -> str: pass
