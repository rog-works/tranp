import functools
from typing import Any, Iterator, TypeVar, cast

from rogw.tranp.ast.dsn import DSN
from rogw.tranp.ast.entry import SourceMap
from rogw.tranp.ast.path import EntryPath
from rogw.tranp.ast.query import Query
from rogw.tranp.errors import LogicError, NotFoundError
from rogw.tranp.lang.implementation import deprecated, injectable, override
from rogw.tranp.lang.sequence import flatten
from rogw.tranp.lang.string import snakelize
from rogw.tranp.module.types import ModulePath
from rogw.tranp.node.embed import EmbedKeys, Meta
from rogw.tranp.node.interface import IDomain, IScope, ITerminal

T_Node = TypeVar('T_Node', bound='Node')


class Node:
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

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		return f'<{self.__class__.__name__}: {self.fullyname}>'

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.full_path}>'

	@override
	def __hash__(self) -> int:
		"""int: オブジェクトのハッシュ値"""
		return hash(self.__repr__())

	@override
	def __eq__(self, other: Any) -> bool:
		"""比較演算子のオーバーロード

		Args:
			other (Any): 比較対象
		Returns:
			bool: True = 同じ
		Raises:
			ValueError: Node以外のオブジェクトを指定
		"""
		if other is None:
			return False

		if not isinstance(other, Node):
			raise ValueError(f'Not allowed comparison. other: {type(other)}')

		return self.__repr__() == other.__repr__()

	@property
	def module_path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path.ref_name

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
	def domain_name(self) -> str:
		"""str: ドメイン名 Note: スコープを除いた自身を表す一意な名称。絶対参照(完全参照名によるアクセス)が不要なノードは無名とする"""
		return ''

	@property
	def fullyname(self) -> str:
		"""完全参照名を取得

		Returns:
			str: 完全参照名
		Note:
			# 命名規則
			* IDomainを実装(ClassDef/Declare/Reference/Type/FuncCall/Literal/Empty): scope.domain_name
			* IScopeを実装(FlowEntry): scope@id
			* その他: scope.classification@id
		"""
		if isinstance(self, IDomain):
			return DSN.join(self.scope, self.domain_name)
		elif isinstance(self, IScope):
			return DSN.identify(self.scope, self.id)
		else:
			return DSN.join(self.scope, DSN.identify(self.classification, self.id))

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
	def can_expand(self) -> bool:
		"""bool: True = 配下の要素を展開"""
		return not isinstance(self, ITerminal)

	@property
	def id(self) -> int:
		"""int: AST上のID"""
		return self.__nodes.id(self.full_path)

	@property
	def source_map(self) -> SourceMap:
		"""SourceMap: ソースマップ"""
		return self.__nodes.source_map(self.full_path)

	@property
	def tokens(self) -> str:
		"""str: 自身のトークン表現"""
		return '.'.join(self._values())

	@property
	def parent(self) -> 'Node':
		"""Node: 親のノード Note: あくまでもノード上の親であり、AST上の親と必ずしも一致しない点に注意"""
		return self.__nodes.parent(self.full_path)

	def prop_keys(self) -> list[str]:
		"""展開プロパティーのメソッド名を取得。対象のプロパティーは埋め込まれたメタデータを基に抽出

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

	def __embed_classes(self, via: type[T_Node]) -> list[type['Node']]:
		"""対象のクラス自身を含む継承関係のあるクラスを基底クラス順に取得。取得されるクラスはメタデータと関連する派生クラスに限定

		Args:
			via (type[T_Node]): 対象のクラス
		Returns:
			list[type[Node]]: クラスリスト
		Note:
			Node以下の基底クラスはメタデータと関わりがないため除外
		"""
		classes = [ctor for ctor in via.__mro__ if issubclass(ctor, Node) and ctor is not Node]
		return list(reversed(classes))

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
		if not self.can_expand:
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
		"""プロパティーを平坦化して展開

		Returns:
			list[Node]: プロパティーのノードリスト
		"""
		nodes: list[Node] = []
		for node_or_list in self.__prop_of_nodes().values():
			if isinstance(node_or_list, list):
				nodes.extend(node_or_list)
			else:
				nodes.append(node_or_list)

		return nodes

	def __prop_of_nodes(self) -> dict[str, 'Node | list[Node]']:
		"""プロパティーを展開

		Returns:
			dict[Node | list[Node]]: プロパティーのノードリスト
		"""
		return {key: getattr(self, key) for key in self.prop_keys()}

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
		via = self._full_path.joined(relative_path)
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
		via = self._full_path.joined(relative_path)
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

	def is_a(self, *ctor: type[T_Node]) -> bool:
		"""指定のクラスと同じか派生クラスか判定

		Args:
			*ctor (type[T_Node]): 判定するクラス
		Returns:
			bool: True = 同種
		"""
		return isinstance(self, ctor)

	def as_a(self, to_class: type[T_Node]) -> T_Node:
		"""指定の具象クラスに変換。変換先が派生クラスの場合のみ変換し、同じか基底クラスの場合は何もしない

		Args:
			to_class (type[T_Node]): 変換先の具象クラス
		Returns:
			T_Node: 具象クラスのインスタンス
		Raises:
			LogicError: 許可されない変換先を指定
		Note:
			## 変換条件
			1. 変換先と継承関係
			2. 受け入れタグが設定
		"""
		if self.is_a(to_class):
			return cast(T_Node, self)

		if not issubclass(to_class, self.__class__):
			raise LogicError(str(self), to_class)

		if not self.__acceptable_by(to_class):
			raise LogicError(str(self), to_class)

		return cast(T_Node, to_class(self.__nodes, self.__module_path, self.full_path))

	def __acceptable_by(self, to_class: type[T_Node]) -> bool:
		"""指定の具象クラスへの変換が受け入れられるか判定

		Args:
			to_class (type[T_Node]): 変換先の具象クラス
		Returns:
			bool: True = 受け入れ出来る
		"""
		accept_tags = self.__accept_tags(to_class)
		return len(accept_tags) == 0 or self.tag in accept_tags

	def __accept_tags(self, to_class: type[T_Node]) -> list[str]:
		"""メタデータより変換先の受け入れタグリストを取得

		Args:
			to_class (type[T_Node]): 変換先の具象クラス
		Returns:
			list[str]: 受け入れタグリスト
		Note:
			派生クラスによって上書きする仕様 @see embed.accept_tags
		"""
		accept_tags: list[str] = []
		for ctor in self.__embed_classes(to_class):
			in_accept_tags = Meta.dig_for_class(Node, ctor, EmbedKeys.AcceptTags, default=[])
			if len(in_accept_tags) > 0:
				accept_tags = in_accept_tags

		return accept_tags

	def one_of(self, expects: type[T_Node]) -> T_Node:
		"""指定のクラスと同じか派生クラスか判定し、合致すればそのままインスタンスを返す。いずれのクラスでもない場合はエラーを出力

		Args:
			expects (T_Node): 期待するクラス(型/共用型)
		Returns:
			T_Node: インスタンス
		Raises:
			LogicError: 指定のクラスと合致しない
		Examples:
			```python
			@property
			def var_type(self) -> Type | Empty:
				return self._at(1).one_of(Type | Empty)
			```
		"""
		if hasattr(expects, '__args__'):
			inherits = [candidate for candidate in getattr(expects, '__args__', []) if isinstance(self, candidate)]
			if len(inherits) == 1:
				return cast(T_Node, self)
		else:
			if self.is_a(expects):
				return cast(T_Node, self)

		raise LogicError(str(self), expects)

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

	def actualize(self: T_Node) -> T_Node:
		"""ASTの相関関係より判断した実体としてより適切な具象クラスのインスタンスに変換。条件は具象側で実装

		Returns:
			T_Node: 具象クラスのインスタンス
		"""
		for feature_class in self._feature_classes():
			if not self.__acceptable_by(feature_class):
				continue

			if feature_class.match_feature(self):
				return self.as_a(feature_class)

		return self

	def dirty_proxify(self: T_Node, **overrides: Any) -> T_Node:
		"""プロキシノードを生成

		Args:
			**overrides (Any): 上書きするプロパティー
		Returns:
			T_Node: プロキシノード
		Note:
			XXX シンボルエイリアスにのみ使う想定。ダーティーな実装のため濫用は厳禁
			XXX classification/source_mapは固定で上書き
		"""
		overrides = {**overrides, 'classification': snakelize(self.__class__.__name__), 'source_map': {'begin': (0, 0), 'end': (0, 0)}}

		class Proxy(self.__class__):
			def __getattribute__(self, __name: str) -> Any:
				if __name in overrides:
					return overrides[__name]

				return super().__getattribute__(__name)

		# XXX 継承関係が無いと判断されるのでcastで対処
		return cast(T_Node, Proxy(self.__nodes, self.__module_path, self.full_path))

	def dirty_child(self, ctor: type[T_Node], entry_tag: str, **overrides: Any) -> T_Node:
		"""仮想の子ノードを生成

		Args:
			ctor (type[T_Node]): 子ノードのクラス
			entry_tag (str): エントリータグ (一意性は呼び出し側で考慮する)
			**overrides (Any): 上書きするプロパティー
		Returns:
			T_Node: 生成した子ノード
		Note:
			XXX 主に空要素として使う想定。ダーティーな実装のため濫用は厳禁
		Examples:
			```python
			@property
			def var_type(self) -> Type | Empty:
				if len(self._children()) == 2:
					return self._at(1)

				return self.dirty_child(Empty, '__empty__', tokens='')
			```
		"""
		child = ctor(self.__nodes, self.__module_path, self._full_path.joined(entry_tag))
		return child.dirty_proxify(**overrides)

	def pretty(self, depth: int = -1) -> str:
		"""階層構造を出力

		Args:
			depth (int): 探索深度。-1は無制限。(default = -1)
		Returns:
			str: 階層構造
		"""
		def expand_lines(node: Node, begin: str, after: str) -> list[str]:
			"""str: ノード内の要素を展開して行リストを返却"""
			lines: list[str] = []
			for j, ln_line in enumerate(node.pretty(depth - 1).split('\n')):
				prefix = begin if j == 0 else after
				lines.append(f'{prefix}{ln_line}')

			return lines

		if not self.can_expand or depth == 0:
			return str(self)

		lines = [str(self)]
		under_props = self.__prop_of_nodes()
		if under_props:
			for i, item in enumerate(under_props.items()):
				key, node_or_list = item
				last_i = i == len(under_props) - 1
				belongs_i = '|' if not last_i else ' '
				if isinstance(node_or_list, list):
					lines.append(f'+-{key}:')
					for j, in_node in enumerate(node_or_list):
						last_j = j == len(node_or_list) - 1
						belongs_j = '|' if not last_j else ' '
						in_lines = expand_lines(in_node, f'{belongs_i} +-', f'{belongs_i} {belongs_j} ')
						lines.extend(in_lines)
				else:
					in_lines = expand_lines(node_or_list, f'+-{key}: ', f'{belongs_i} ')
					lines.extend(in_lines)

			return '\n'.join(lines)
		else:
			under = self._under_expand()
			for i, node in enumerate(under):
				last_i = i == len(under_props) - 1
				belongs_i = '|' if not last_i else ' '
				in_lines = expand_lines(node, '+-', f'{belongs_i} ')
				lines.extend(in_lines)

			return '\n'.join(lines)

	# XXX def is_statement(self) -> bool: pass
	# XXX def serialize(self) -> dict: pass
