from enum import Enum
from typing import Protocol

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.syntax.node.node import Node


class AliasHandler(Protocol):
	"""エイリアス解決ハンドラープロトコル"""

	def __call__(self, key: str, fallback: str = '') -> str:
		"""キーに対応する文字列に変換

		Args:
			key: エイリアスキー
			fallback: 存在しない場合の代用値 (default = '')
		Returns:
			エイリアス
		Note:
			```
			@see rogw.tranp.dsn.translation.alias_dsn
			@see i18n.I18n.t
			```
		"""
		...


class AliasTranspiler(Protocol):
	"""エイリアストランスパイラープロトコル"""

	def __call__(self, node: Node) -> str:
		"""ノードからエイリアスにトランスパイル

		Args:
			node: エイリアスノード
		Returns:
			エイリアス
		Note:
			@see rogw.tranp.transpiler.types.ITranspiler
		"""
		...


class PathMethods(Enum):
	"""パス生成方式"""
	Domain = 'domain'
	Fully = 'fully'
	Accessible = 'accessible'


class ClassDomainNaming:
	"""クラスのドメイン名生成モジュール"""

	@classmethod
	def domain_name(cls, types: defs.ClassDef, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスのドメイン名を生成

		Args:
			types: クラス宣言ノード
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			ドメイン名
		"""
		if alias_handler:
			return alias_handler(alias_dsn(types.fullyname), fallback=cls.__alias_or_domain_name(types, alias_transpiler))

		return cls.__alias_or_domain_name(types, alias_transpiler)

	@classmethod
	def fullyname(cls, types: defs.ClassDef, alias_handler: AliasHandler | None) -> str:
		"""クラスの完全参照名を生成

		Args:
			types: クラス宣言ノード
			alias_handler: エイリアス解決ハンドラー
		Returns:
			完全参照名
		Note:
			XXX 完全参照名はエイリアス化前の名前で登録されるため、AliasTranspilerは指定しない
		"""
		return DSN.join(types.module_path, cls.__namespace(types, alias_handler, None), cls.domain_name(types, alias_handler, None))

	@classmethod
	def accessible_name(cls, types: defs.ClassDef, alias_handler: AliasHandler | None , alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスの名前空間上の参照名を生成

		Args:
			types: クラス宣言ノード
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			名前空間上の参照名
		"""
		return DSN.join(cls.__namespace(types, alias_handler, alias_transpiler), cls.domain_name(types, alias_handler, alias_transpiler))

	@classmethod
	def make_manualy(cls, types: defs.ClassDef, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None, path_method: PathMethods = PathMethods.Domain) -> str:
		"""クラスのドメイン名を生成

		Args:
			types: クラス宣言ノード
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
			path_method: パス生成方式 (default = Domain)
		Returns:
			ドメイン名
		"""
		if path_method == PathMethods.Fully:
			return cls.fullyname(types, alias_handler)
		if path_method == PathMethods.Accessible:
			return cls.accessible_name(types, alias_handler, alias_transpiler)
		else:
			return cls.domain_name(types, alias_handler, alias_transpiler)

	@classmethod
	def __alias_or_domain_name(cls, types: defs.ClassDef, alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスのドメイン名を解決

		Args:
			types: クラス宣言ノード
			alias_transpiler: エイリアストランスパイラー
		Returns:
			ドメイン名
		"""
		if not alias_transpiler:
			return types.domain_name

		embedder = types.alias_embedder
		if not embedder:
			return types.domain_name

		alias_node = embedder.arguments[0].value
		alias = alias_node.as_string if isinstance(alias_node, defs.String) else alias_transpiler(alias_node)[1:-1]
		is_prefix = len(embedder.arguments) == 2
		return f'{alias}{types.domain_name}' if is_prefix else alias

	@classmethod
	def __namespace(cls, types: defs.ClassDef, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスの名前空間を生成

		Args:
			types: クラス宣言ノード
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			名前空間
		"""
		if not alias_handler:
			return DSN.shift(DSN.relativefy(types.namespace, types.module_path), -1)

		return DSN.join(*[cls.domain_name(ancestor, alias_handler, alias_transpiler) for ancestor in cls.__ancestor_classes(types)])

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
	def domain_name(cls, raw: IReflection, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスの短縮表記を生成(ドメイン名)

		Args:
			raw: シンボル
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, alias_handler, alias_transpiler, PathMethods.Domain)

	@classmethod
	def fullyname(cls, raw: IReflection, alias_handler: AliasHandler | None) -> str:
		"""クラスの短縮表記を生成(完全参照名)

		Args:
			raw: シンボル
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, alias_handler, None, PathMethods.Fully)

	@classmethod
	def accessible_name(cls, raw: IReflection, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None) -> str:
		"""クラスの短縮表記を生成(名前空間上の参照名)

		Args:
			raw: シンボル
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
		Returns:
			短縮表記
		"""
		return cls.__make_general(raw, alias_handler, alias_transpiler, PathMethods.Accessible)

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
		return cls.__make_decorate(raw, None, None, PathMethods.Domain)

	@classmethod
	def __make_general(cls, raw: IReflection, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None, path_method: PathMethods) -> str:
		"""クラスの短縮表記を生成(一般型)

		Args:
			raw: シンボル
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
			path_method: パス生成方式
		Returns:
			短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, alias_handler, alias_transpiler, path_method)
		if len(raw.attrs) == 0 or raw.types.is_a(defs.AltClass):
			return symbol_name

		attrs = [cls.__make_general(attr, alias_handler, alias_transpiler, path_method) for attr in raw.attrs]
		return f'{symbol_name}<{", ".join(attrs)}>'

	@classmethod
	def __make_decorate(cls, raw: IReflection, alias_handler: AliasHandler | None, alias_transpiler: AliasTranspiler | None, path_method: PathMethods) -> str:
		"""クラスの短縮表記を生成(装飾型)

		Args:
			raw: シンボル
			alias_handler: エイリアス解決ハンドラー
			alias_transpiler: エイリアストランスパイラー
			path_method: パス生成方式
		Returns:
			短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, alias_handler, alias_transpiler, path_method)
		if len(raw.attrs) == 0:
			return symbol_name

		if raw.types.is_a(defs.AltClass):
			attrs = [cls.__make_decorate(attr, alias_handler, alias_transpiler, path_method) for attr in raw.attrs]
			return f'{symbol_name}={attrs[0]}'
		elif raw.types.is_a(defs.Function):
			attrs = [cls.__make_decorate(attr, alias_handler, alias_transpiler, path_method) for attr in raw.attrs]
			return f'{symbol_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
		else:
			attrs = [cls.__make_decorate(attr, alias_handler, alias_transpiler, path_method) for attr in raw.attrs]
			return f'{symbol_name}<{", ".join(attrs)}>'
