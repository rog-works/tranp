from enum import Enum
from typing import Protocol

import tranp.app.syntax.node.definition as defs
from tranp.app.compatible.python.embed import Embed
from tranp.app.dsn.dsn import DSN
from tranp.app.dsn.translation import alias_dsn
from tranp.app.semantics.reflection.base import IReflection
from tranp.app.syntax.node.node import Node


class AliasHandler(Protocol):
	"""プロトコル(エイリアス解決)"""

	def __call__(self, key: str, fallback: str = '') -> str:
		"""キーに対応する文字列に変換

		Args:
			key: エイリアスキー
			fallback: 存在しない場合の代用値 (default = '')
		Returns:
			エイリアス
		Note:
			```
			@see tranp.app.dsn.translation.alias_dsn
			@see i18n.I18n.t
			```
		"""
		...


class AliasTranspiler(Protocol):
	"""プロトコル(トランスパイル)"""

	def __call__(self, node: Node) -> str:
		"""ノードからエイリアスにトランスパイル

		Args:
			node: エイリアスノード
		Returns:
			エイリアス
		Note:
			@see tranp.app.transpiler.types.ITranspiler
		"""
		...


class AliasDoneDomain(Protocol):
	"""プロトコル(ドメイン名確定)"""

	def __call__(self, domain_name: str) -> str:
		"""ドメイン名を確定

		Args:
			domain_name: ドメイン名
		Returns:
			確定後のドメイン名
		"""
		...


class AliasBundler:
	"""エイリアス解決バンドラー"""

	def __init__(self, t: AliasHandler, transpile: AliasTranspiler, done: AliasDoneDomain) -> None:
		"""インスタンスを生成

		Args:
			t: エイリアス解決
			transpile: トランスパイル
			done: ドメイン確定
		"""
		self.t = t
		self.transpile = transpile
		self.done = done


class PathMethods(Enum):
	"""パス生成方式"""
	Domain = 'domain'
	Fully = 'fully'
	Accessible = 'accessible'


class ClassDomainNaming:
	"""クラスのドメイン名生成モジュール"""

	@classmethod
	def domain_name(cls, types: defs.ClassDef, bundler: AliasBundler | None) -> str:
		"""クラスのドメイン名を生成

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			ドメイン名
		"""
		if bundler:
			return bundler.t(alias_dsn(types.fullyname), fallback=cls.__alias_or_domain_name(types, bundler))

		return cls.__alias_or_domain_name(types, bundler)

	@classmethod
	def fullyname(cls, types: defs.ClassDef, bundler: AliasBundler | None) -> str:
		"""クラスの完全参照名を生成

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			完全参照名
		"""
		return DSN.join(types.module_path, cls.__namespace(types, bundler), cls.domain_name(types, bundler))

	@classmethod
	def accessible_name(cls, types: defs.ClassDef, bundler: AliasBundler | None) -> str:
		"""クラスの名前空間上の参照名を生成

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			名前空間上の参照名
		"""
		return DSN.join(cls.__namespace(types, bundler), cls.domain_name(types, bundler))

	@classmethod
	def make_manualy(cls, types: defs.ClassDef, bundler: AliasBundler | None, path_method: PathMethods = PathMethods.Domain) -> str:
		"""クラスのドメイン名を生成

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
			path_method: パス生成方式 (default = Domain)
		Returns:
			ドメイン名
		"""
		if path_method == PathMethods.Fully:
			return cls.fullyname(types, bundler)
		if path_method == PathMethods.Accessible:
			return cls.accessible_name(types, bundler)
		else:
			return cls.domain_name(types, bundler)

	@classmethod
	def __alias_or_domain_name(cls, types: defs.ClassDef, bundler: AliasBundler | None) -> str:
		"""クラスのドメイン名を解決

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			ドメイン名
		"""
		if not bundler:
			return types.domain_name

		embedder = types.alias_embedder
		if not embedder:
			return types.domain_name

		alias_node = embedder.arguments[0].value
		alias = alias_node.as_string if isinstance(alias_node, defs.String) else bundler.transpile(alias_node)[1:-1]
		is_prefix = len(embedder.arguments) == 2
		return f'{alias}{types.domain_name}' if is_prefix else alias

	@classmethod
	def __namespace(cls, types: defs.ClassDef, bundler: AliasBundler | None) -> str:
		"""クラスの名前空間を生成

		Args:
			types: クラス宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			名前空間
		"""
		if not bundler:
			return DSN.shift(DSN.relativefy(types.namespace, types.module_path), -1)

		return DSN.join(*[cls.domain_name(ancestor, bundler) for ancestor in cls.__ancestor_classes(types)])

	@classmethod
	def __ancestor_classes(cls, types: defs.ClassDef) -> list[defs.ClassDef]:
		"""名前空間を持つ親クラスを再帰的に抽出

		Args:
			types: 起点のクラス宣言ノード
		Returns:
			親クラスのノードリスト
		Note:
			FIXME 設計的にはIScopeを判断材料とするべき
		"""
		curr = types.parent
		ancestors: list[defs.ClassDef] = []
		while not isinstance(curr, defs.Entrypoint):
			if isinstance(curr, defs.ClassDef):
				ancestors.insert(0, curr)

			curr = curr.parent

		return ancestors


class PropNaming:
	"""プロパティー名生成モジュール"""

	@classmethod
	def to_prop_name(cls, decl: defs.DeclVars, bundler: AliasBundler) -> str:
		"""定義ノードからプロパティーの名前を取得

		Args:
			decl: 変数宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			プロパティー名
		"""
		embedder = cls.__analyze_embedder(decl)
		if embedder:
			return bundler.done(cls.__from_embedder(decl, bundler, embedder))
		else:
			return bundler.done(cls.__from_decl(decl, bundler))

	@classmethod
	def __analyze_embedder(cls, decl: defs.DeclVars) -> defs.FuncCall | None:
		"""プロパティー名の埋め込みを解析

		Args:
			decl: 変数宣言ノード
		Returns:
			関数コールノード(Embed.alias) | None
		"""
		declare: defs.AnnoAssign | None = None
		if isinstance(decl.declare, defs.AnnoAssign):
			declare = decl.declare
		elif isinstance(decl, defs.DeclThisVar):
			# クラス自身が所有している変数のみが対象
			decl_this_vars = decl.class_types.as_a(defs.Class).decl_this_vars
			if decl.domain_name in decl_this_vars:
				declare = decl_this_vars[decl.domain_name]

		if not declare:
			return None

		for annotation in declare.var_type.annotations:
			if isinstance(annotation, defs.FuncCall) and annotation.calls.tokens == Embed.alias.__qualname__:
				return annotation

		return None

	@classmethod
	def __from_decl(cls, decl: defs.DeclVars, bundler: AliasBundler) -> str:
		"""プロパティー名を解決(オリジナル/翻訳)

		Args:
			decl: 変数宣言ノード
			bundler: エイリアス解決バンドラー
		Returns:
			プロパティー名
		"""
		return bundler.t(alias_dsn(decl.fullyname), fallback=decl.domain_name)

	@classmethod
	def __from_embedder(cls, decl: defs.DeclVars, bundler: AliasBundler, embedder: defs.FuncCall) -> str:
		"""プロパティー名を解決(埋め込み)

		Args:
			decl: 変数宣言ノード
			bundler: エイリアス解決バンドラー
			embedder: 関数コールノード(Embed.alias)
		Returns:
			プロパティー名
		"""
		alias_node = embedder.arguments[0]
		alias_name = alias_node.as_string if isinstance(alias_node, defs.String) else bundler.transpile(alias_node)[1:-1]
		if len(embedder.arguments) == 1:
			return alias_name

		origin_name = cls.__from_decl(decl, bundler)
		return f'{alias_name}{origin_name}'


class ClassShorthandNaming:
	"""クラスの短縮表記生成モジュール

	Note:
		```
		### 書式
		* types=AltClass: '${alias}=${actual}'
		* types=Function: '${domain_name}(...${arguments}) -> ${return}'
		* その他: '${domain_name}<...${attributes}>'
		```
	"""

	@classmethod
	def domain_name(cls, raw: IReflection, bundler: AliasBundler) -> str:
		"""クラスの短縮表記を生成(ドメイン名)

		Args:
			raw: シンボル
			bundler: エイリアス解決バンドラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, bundler, PathMethods.Domain)

	@classmethod
	def fullyname(cls, raw: IReflection, bundler: AliasBundler) -> str:
		"""クラスの短縮表記を生成(完全参照名)

		Args:
			raw: シンボル
			bundler: エイリアス解決バンドラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, bundler, PathMethods.Fully)

	@classmethod
	def accessible_name(cls, raw: IReflection, bundler: AliasBundler) -> str:
		"""クラスの短縮表記を生成(名前空間上の参照名)

		Args:
			raw: シンボル
			bundler: エイリアス解決バンドラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, bundler, PathMethods.Accessible)

	@classmethod
	def domain_name_for_debug(cls, raw: IReflection) -> str:
		"""クラスの短縮表記を生成(ドメイン名/デバッグ用)

		Args:
			raw: シンボル
		Returns:
			短縮表記
		Note:
			XXX エイリアス化前の名前になる点に注意
		"""
		return cls.__make_decorate(raw, None, PathMethods.Domain)

	@classmethod
	def __make_general(cls, raw: IReflection, bundler: AliasBundler | None, path_method: PathMethods) -> str:
		"""クラスの短縮表記を生成(一般型)

		Args:
			raw: シンボル
			bundler: エイリアス解決バンドラー
			path_method: パス生成方式
		Returns:
			短縮表記
		"""
		attrs = raw.attrs
		symbol_name = ClassDomainNaming.make_manualy(raw.types, bundler, path_method)
		if len(attrs) == 0 or raw.types.is_a(defs.AltClass):
			return symbol_name

		attrs_str = [cls.__make_general(attr, bundler, path_method) for attr in attrs]
		return f'{symbol_name}<{", ".join(attrs_str)}>'

	@classmethod
	def __make_decorate(cls, raw: IReflection, bundler: AliasBundler | None, path_method: PathMethods) -> str:
		"""クラスの短縮表記を生成(装飾型)

		Args:
			raw: シンボル
			bundler: エイリアス解決バンドラー
			path_method: パス生成方式
		Returns:
			短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, bundler, path_method)
		if len(raw.attrs) == 0:
			return symbol_name

		if raw.types.is_a(defs.AltClass):
			attrs = [cls.__make_decorate(attr, bundler, path_method) for attr in raw.attrs]
			return f'{symbol_name}={attrs[0]}'
		elif raw.types.is_a(defs.Function):
			attrs = [cls.__make_decorate(attr, bundler, path_method) for attr in raw.attrs]
			return f'{symbol_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
		else:
			attrs = [cls.__make_decorate(attr, bundler, path_method) for attr in raw.attrs]
			return f'{symbol_name}<{", ".join(attrs)}>'
