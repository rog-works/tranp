import functools
from typing import Any, Iterator, Literal, TypeVar, cast

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.errors import LogicError
from rogw.tranp.io.memo2 import Memoize
from rogw.tranp.lang.annotation import deprecated, injectable, override
from rogw.tranp.lang.sequence import flatten
from rogw.tranp.lang.string import snakelize
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entry import SourceMap
from rogw.tranp.syntax.ast.path import EntryPath
from rogw.tranp.syntax.ast.query import Query
from rogw.tranp.syntax.errors import IllegalConvertionError, NodeNotFoundError
from rogw.tranp.syntax.node.embed import EmbedKeys, Meta
from rogw.tranp.syntax.node.behavior import IDomain, INamespace, IScope, ITerminal

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
		self._memo = Memoize()

	@override
	def __str__(self) -> str:
		"""str: オブジェクトの文字列表現"""
		source_map = self.source_map
		source_map_begin = ', '.join(map(str, source_map['begin']))
		source_map_end = ', '.join(map(str, source_map['end']))
		joined_source_map = f'({source_map_begin})..({source_map_end})'
		return f'<{self.__class__.__name__}: @{self.id} {self.fullyname} {joined_source_map}>'

	@override
	def __repr__(self) -> str:
		"""str: オブジェクトのシリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.module_path} {self.full_path}>'

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
			LogicError: Node以外のオブジェクトを指定 XXX 出力する例外は要件等
		"""
		if other is None:
			return False

		if not isinstance(other, Node):
			raise LogicError(f'Not allowed comparison. other: {type(other)}')

		return self.__repr__() == other.__repr__()

	@property
	def module_path(self) -> str:
		"""str: モジュールパス"""
		return self.__module_path.path

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
			* その他: scope.classification@id
		"""
		def factory() -> str:
			if isinstance(self, IDomain):
				return ModuleDSN.full_joined(self.scope, self.domain_name)
			else:
				return ModuleDSN.identify(ModuleDSN.full_joined(self.scope, self.classification), self.id)

		return self._memo.get('fullyname', factory)

	@property
	def scope(self) -> str:
		"""str: 自身が所属するスコープ"""
		def factory() -> str:
			parent = self.parent
			if isinstance(parent, IScope):
				return ModuleDSN.full_joined(parent.scope, parent.domain_name or parent.classification)
			else:
				return parent.scope

		return self._memo.get('scope', factory)

	@property
	def namespace(self) -> str:
		"""str: 自身が所属する名前空間"""
		def factory() -> str:
			parent = self.parent
			if isinstance(parent, INamespace):
				return ModuleDSN.full_joined(parent.namespace, parent.domain_name)
			else:
				return parent.namespace

		return self._memo.get('namespace', factory)

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
		"""展開プロパティーのメソッド名を取得

		Returns:
			list[str]: 展開プロパティーのメソッド名リスト
		Note:
			@see embed.expandable
		"""
		prop_keys: list[str] = []
		for ctor in self.__embed_classes(self.__class__):
			meta = Meta.dig_for_method(Node, ctor, EmbedKeys.Expandable, value_type=bool)
			prop_keys = [*prop_keys, *[name for name, _ in meta.items()]]

		return prop_keys

	def accept_tags(self) -> list[str]:
		"""受け入れタグリストを取得

		Returns:
			list[str]: 受け入れタグリスト
		Note:
			派生クラスによって上書きする仕様
			@see embed.accept_tags
		"""
		accept_tags: list[str] = []
		for ctor in self.__embed_classes(self.__class__):
			in_accept_tags = Meta.dig_for_class(Node, ctor, EmbedKeys.AcceptTags, default=[])
			if len(in_accept_tags) > 0:
				accept_tags = in_accept_tags

		return accept_tags

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

	def procedural(self, order: Literal['flow', 'ast'] = 'flow') -> list['Node']:
		"""下位のノードを再帰的に展開し、1次元に平坦化して取得

		Args:
			order (Literal['flow' | 'ast']): 並び順 (default = 'flow')
		Returns:
			list[Node]: ノードリスト
		Note:
			# orderの使い分け
			* 'flow': ノードのプロパティーの定義順で出力する場合
			* 'ast': ASTの評価順序で出力する場合
		"""
		return self.__procedural_flow() if order == 'flow' else self.__procedural_ast()

	def __procedural_flow(self) -> list['Node']:
		"""下位のノードを再帰的に展開し、1次元に平坦化して取得(プロパティー定義順)

		Returns:
			list[Node]: ノードリスト
		Note:
			# 優先順位
			1. 終端要素は空を返す
			2. 展開プロパティーのノードを使う
			3. 下位ノードを使う
		"""
		if not self.can_expand:
			return []

		under = self.__prop_expand() or self._under_expand()
		return list(flatten([[node, *node.procedural()] for node in under]))

	def __procedural_ast(self) -> list['Node']:
		"""下位のノードを再帰的に展開し、1次元に平坦化して取得(AST準拠)

		Returns:
			list[Node]: ノードリスト
		Note:
			flattenとの相違点は並び順のみ
		"""
		path_of_nodes = {node.full_path: node for node in self.__procedural_flow()}
		sorted_paths = self.__ast_order(enumerate(path_of_nodes.keys()))
		return [path_of_nodes[full_path] for full_path in sorted_paths]

	def __ast_order(self, index_of_paths: Iterator[tuple[int, str]]) -> list[str]:
		"""インデックスとフルパスを元にASTの評価順序にソート

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
			NodeNotFoundError: ノードが存在しない
		"""
		return self.__nodes.by(self._full_path.joined(relative_path))

	def _at(self, index: int) -> 'Node':
		"""指定のインデックスの子ノードをフェッチ

		Args:
			index (int): 子のインデックス
		Returns:
			Node: ノード
		Raises:
			NodeNotFoundError: ノードが存在しない
		"""
		children = self._children()
		if index < 0 or len(children) <= index:
			raise NodeNotFoundError(str(self), index)

		return children[index]

	@deprecated
	def _at_child(self, index: int) -> 'Node':
		"""展開できる子ノードをフェッチ

		Args:
			index (int): 子のインデックス
		Returns:
			Node: ノード
		Raises:
			NodeNotFoundError: 子が存在しない
		"""
		under = self._under_expand()
		if index < 0 or len(under) <= index:
			raise NodeNotFoundError(str(self), index)

		return under[index]

	@deprecated
	def _siblings(self, relative_path: str = '') -> list['Node']:
		"""指定のパスを基準に同階層のノードをフェッチ
		パスを省略した場合は自身と同階層を検索し、自身を除いたノードを返却

		Args:
			relative_path (str): 自身のノードからの相対パス(default = '')
		Returns:
			list[Node]: ノードリスト
		Raises:
			NodeNotFoundError: 基点のノードが存在しない
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
			NodeNotFoundError: 基点のノードが存在しない
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
			NodeNotFoundError: ノードが存在しない
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

	def as_a(self, expect: type[T_Node]) -> T_Node:
		"""指定のクラスと同じか派生クラスか判定し、合致すればそのままインスタンスを返す。継承関係の無いクラスを指定すると例外を出力

		Args:
			expect (type[T_Node]): 期待するクラス
		Returns:
			T_Node: インスタンス
		Raises:
			IllegalConvertionError: 許可されない変換先を指定
		"""
		if self.is_a(expect):
			return cast(T_Node, self)

		raise IllegalConvertionError(str(self), expect)

	def one_of(self, *expects: type[T_Node]) -> T_Node:
		"""指定のクラスと同じか派生クラスか判定し、合致すればそのままインスタンスを返す。合致するクラスが1件以外の場合は例外を出力

		Args:
			*expects (type[T_Node]): 期待するクラス(型/共用型)
		Returns:
			T_Node: インスタンス
		Raises:
			IllegalConvertionError: 合致するクラスが1件以外
		Examples:
			```python
			@property
			def var_type(self) -> Type | Empty:
				return self._at(1).one_of(Type, Empty)
			```
		"""
		inherits = [candidate for candidate in expects if isinstance(self, candidate)]
		if len(inherits) == 1:
			return cast(T_Node, self)

		raise IllegalConvertionError(str(self), expects)

	@classmethod
	def match_feature(cls, via: 'Node') -> bool:
		"""引数のノードが自身の特徴と一致するか判定
		一致すると判断されたノードはResolverより実体化される
		条件判定は派生クラス側で実装

		Args:
			via (Node): 変換前のノード
		Returns:
			bool: True = 一致
		Note:
			## 注意点
			このメソッド内で引数のviaを元に親ノードをインスタンス化すると無限ループするため、その様に実装してはならない
			```python
			# OK
			return via._full_path.shift(-1).last_tag == 'xxx'
			# NG
			return via.parent.tag == 'xxx'
			```
		"""
		return True

	def dirty_proxify(self: T_Node, **overrides: Any) -> T_Node:
		"""プロキシノードを生成

		Args:
			**overrides (Any): 上書きするプロパティー
		Returns:
			T_Node: プロキシノード
		Note:
			XXX ダーティーな実装のため濫用は厳禁
			XXX classification/source_mapは固定で上書き
		"""
		source_map: SourceMap = {'begin': (0, 0), 'end': (0, 0)}
		overrides = {**overrides, 'classification': snakelize(self.__class__.__name__), 'source_map': source_map}

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
			for j, in_line in enumerate(node.pretty(depth - 1).split('\n')):
				prefix = begin if j == 0 else after
				lines.append(f'{prefix}{in_line}')

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
