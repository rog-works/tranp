import functools
from typing import Iterator, cast

from py2cpp.ast.dsn import DSN
from py2cpp.ast.path import EntryPath
from py2cpp.ast.query import Query
from py2cpp.errors import LogicError, NotFoundError
from py2cpp.lang.annotation import deprecated, injectable
from py2cpp.lang.sequence import flatten
from py2cpp.lang.string import snakelize
from py2cpp.module.types import ModulePath
from py2cpp.node.base import NodeBase, T_NodeBase
from py2cpp.node.embed import EmbedKeys, Meta
from py2cpp.node.interface import IScope, ITerminal


class Node(NodeBase):
	"""ASTのエントリーと紐づくノードの基底クラス
	自身のエントリーを基点にJSONPathクエリーベースで各ノードへ参照が可能
	派生クラスではノードの役割をプロパティーとして定義する

	Note:
		ASTを役割に適した形に単純化するため、AST上の余分な階層構造は排除する
		そのため、必ずしもAST上のエントリーとノードのアライメントは一致しない点に注意
	"""

	@injectable
	def __init__(self, nodes: Query['Node'], module_path: ModulePath, full_path: str) -> None:
		"""インスタンスを生成

		Args:
			nodes (Query[Node]): クエリーインターフェイス @inject
			module_path (ModulePath): モジュールパス @inject
			full_path (str): ルート要素からのフルパス
		"""
		self.__nodes = nodes
		self.__module_path = module_path
		self._full_path = EntryPath(full_path)

	def __str__(self) -> str:
		"""str: 文字列表現を取得"""
		return f'<{self.__class__.__name__}: {self.full_path}>'

	@property
	def module_path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path

	@property
	def full_path(self) -> str:
		"""str: ルート要素からのフルパス"""
		return self._full_path.origin

	@property
	def tag(self) -> str:
		"""str: エントリータグ。Grammar上のルール名 Note: あくまでもマッチパターンに対するタグであり、必ずしも共通の構造を表さない点に注意"""
		return self._full_path.last_tag

	@property
	def classification(self) -> str:
		"""str: 構造を分類する識別子。実質的に派生クラスに対する識別子"""
		return snakelize(self.__class__.__name__)

	@property
	def public_name(self) -> str:
		"""str: 公開名称 Note: シンボル名(クラス・関数名)を表す。それ以外のノードでは空文字。実装対象: クラス/ファンクション"""
		return ''

	@property
	def is_terminal(self) -> bool:
		"""bool: 終端要素。これ以上展開が不要な要素であることを表す Note: 終端記号とは別"""
		return isinstance(self, ITerminal)

	@property
	def scope(self) -> str:
		"""str: 自身が所有するスコープ。FQDNに相当"""
		if isinstance(self, IScope):
			return DSN.join(self.parent.scope, self.scope_part)
		else:
			return self.parent.scope

	@property
	def namespace(self) -> str:
		"""str: 自身が所有する名前空間。スコープのエイリアス"""
		if isinstance(self, IScope):
			return DSN.join(self.parent.namespace, self.namespace_part)
		else:
			return self.parent.namespace

	@property
	def tokens(self) -> str:
		"""str: 自身のトークン表現"""
		return '.'.join(self._values())

	@property
	def parent(self) -> 'Node':
		"""Node: 親のノード Note: あくまでもノード上の親であり、AST上の親と必ずしも一致しない点に注意"""
		return self.__nodes.parent(self.full_path)

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
				* 終端記号に紐づくノードが欲しい場合は_under_expand
				* 下位のノードを全て洗い出す場合はflatten
				* ASTの計算順序の並びで欲しい場合はcalculated
		"""
		if self.is_terminal:
			return []

		under = self.__prop_expand() or self._under_expand()
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

	def __prop_expand(self) -> list['Node']:
		"""展開プロパティーからノードリストを取得

		Returns:
			list[Node]: 展開プロパティーのノードリスト
		"""
		nodes: list[Node] = []
		for key in self.__expandable_keys():
			func_or_result = getattr(self, key)
			result = cast(Node | list[Node], func_or_result() if callable(func_or_result) else func_or_result)
			nodes.extend(result if type(result) is list else [cast(Node, result)])

		return nodes

	def __expandable_keys(self) -> list[str]:
		"""メタデータより展開プロパティーのメソッド名を抽出

		Returns:
			list[str]: 展開プロパティーのメソッド名リスト
		Note:
			@see trans.node.embed.expandable
		"""
		prop_keys: list[str] = []
		for ctor in self.__embed_classes(self.__class__):
			meta = Meta.dig_for_method(Node, ctor, EmbedKeys.Expandable, value_type=bool)
			prop_keys = [*prop_keys, *[name for name, _ in meta.items()]]

		return prop_keys

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
			relative_path (str): 自身のノードからの相対パス
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
			raise NotFoundError(str(self), index)

		return children[index]

	@deprecated
	def _at_child(self, index: int) -> 'Node':
		"""展開できる子ノードをフェッチ

		Args:
			index (int): 子のインデックス
		Returns:
			Node: ノード
		Raises:
			NotFoundError: 子が存在しない
		"""
		under = self._under_expand()
		if index < 0 or len(under) <= index:
			raise NotFoundError(str(self), index)

		return under[index]

	def _siblings(self, relative_path: str = '') -> list['Node']:
		"""指定のパスを基準に同階層のノードをフェッチ
		パスを省略した場合は自身と同階層を検索し、自身を除いたノードを返却

		Args:
			relative_path (str): 自身のノードからの相対パス(default = '')
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
			relative_path (str): 自身のノードからの相対パス(default = '')
		Returns:
			list[Node]: ノードリスト
		Raises:
			NotFoundError: 基点のノードが存在しない
		"""
		via = self._full_path.joined(relative_path) if relative_path else self.full_path
		return self.__nodes.children(via)

	def _ancestor(self, tag: str) -> 'Node':
		"""指定のエントリータグを持つ直近の親ノードをフェッチ

		Args:
			tag (str): エントリータグ
		Returns:
			Node: ノード
		Raises:
			NotFoundError: ノードが存在しない
		"""
		return self.__nodes.ancestor(self.full_path, tag)

	def _under_expand(self) -> list['Node']:
		"""配下に存在する展開が可能なノードをフェッチ

		Returns:
			list[Node]: ノードリスト
		"""
		return self.__nodes.expand(self.full_path)

	def _values(self) -> list[str]:
		"""自身と配下のエントリーの値を取得

		Returns:
			list[str]: 値リスト
		"""
		return self.__nodes.values(self.full_path)

	def as_a(self, to_class: type[T_NodeBase]) -> T_NodeBase:
		"""指定の具象クラスに変換。変換先が派生クラスの場合のみ変換し、同じか基底クラスの場合は何もしない

		Args:
			to_class (type[T_NodeBase]): 変換先の具象クラス
		Returns:
			T_NodeBase: 具象クラスのインスタンス
		Raises:
			LogicError: 許可されない変換先を指定
		Note:
			## 変換条件
			1. 変換先と継承関係
			2. 受け入れタグが設定
		"""
		if self.is_a(to_class):
			return cast(T_NodeBase, self)

		if not issubclass(to_class, self.__class__):
			raise LogicError(str(self), to_class)

		if not self.__acceptable_by(to_class):
			raise LogicError(str(self), to_class)

		return cast(T_NodeBase, to_class(self.__nodes, self.__module_path, self.full_path))

	def __acceptable_by(self, to_class: type[NodeBase]) -> bool:
		"""指定の具象クラスへの変換が受け入れられるか判定

		Args:
			to_class (type[NodeBase]): 変換先の具象クラス
		Returns:
			list[str]: 受け入れタグリスト
		"""
		accept_tags = self.__accept_tags(to_class)
		return len(accept_tags) == 0 or self.tag in accept_tags

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

	def one_of(self, expects: type[T_NodeBase]) -> T_NodeBase:
		"""指定のクラスと同じか派生クラスか判定し、合致すればそのままインスタンスを返す。いずれのクラスでもない場合はエラーを出力

		Args:
			expects (T_NodeBase): 期待するクラス(型/共用型)
		Returns:
			T_NodeBase: インスタンス
		Raises:
			LogicError: 指定のクラスと合致しない
		Examples:
			```python
			@property
			def var_type(self) -> Symbol | GenericType | Null:
				return self._at(1).one_of(Symbol | GenericType | Null)
			```
		"""
		if hasattr(expects, '__args__'):
			inherits = [candidate for candidate in getattr(expects, '__args__', []) if isinstance(self, candidate)]
			if len(inherits) == 1:
				return cast(T_NodeBase, self)
		else:
			if self.is_a(expects):
				return cast(T_NodeBase, self)

		raise LogicError(str(self), expects)

	def is_a(self, *ctor: type[NodeBase]) -> bool:
		"""指定のクラスと同じか派生クラスか判定

		Args:
			*ctor (type[NodeBase]): 判定するクラス
		Returns:
			bool: True = 同種
		"""
		return isinstance(self, ctor)

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
			@see actualize, _feature_classes
			## 注意点
			このメソッド内で引数のviaを元に親ノードをインスタンス化すると無限ループするため、その様に実装してはならない
			```python
			# OK
			return via._full_path.shift(-1).last_tag == 'xxx'
			# NG
			return via.parent.tag == 'xxx'
			```
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
			if not self.__acceptable_by(feature_class):
				continue

			if feature_class.match_feature(self):
				return self.as_a(feature_class)

		return self

	# XXX def is_statement(self) -> bool: pass
	# XXX def pretty(self) -> str: pass
	# XXX def serialize(self) -> dict: pass
