from enum import Enum
from typing import Protocol

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.semantics.reflection.interface import IReflection
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


class AliasHandler(Protocol):
	"""エイリアス解決ハンドラープロトコル"""

	def __call__(self, key: str, fallback: str = '') -> str:
		"""キーに対応する文字列に変換

		Args:
			key (str): エイリアスキー
			fallback (str): 存在しない場合の代用値 (default = '')
		Returns:
			str: エイリアス
		Note:
			@see dsn.translation.alias_dsn
			@see i18n.I18n.t
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
	def domain_name(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None) -> str:
		"""クラスのドメイン名を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: ドメイン名
		"""
		return alias_handler(alias_dsn(types.fullyname), fallback=types.domain_name) if alias_handler else types.domain_name

	@classmethod
	def fullyname(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの完全参照名を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 完全参照名
		"""
		return DSN.join(types.module_path, cls.__namespace(types, alias_handler), cls.domain_name(types, alias_handler))

	@classmethod
	def accessible_name(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの名前空間上の参照名を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 名前空間上の参照名
		"""
		return DSN.join(cls.__namespace(types, alias_handler), cls.domain_name(types, alias_handler))

	@classmethod
	def make_manualy(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None, path_method: PathMethods = PathMethods.Domain) -> str:
		"""クラスのドメイン名を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
			path_method (PathMethods): パス生成方式 (default = Domain)
		Returns:
			str: ドメイン名
		"""
		if path_method == PathMethods.Fully:
			return cls.fullyname(types, alias_handler)
		if path_method == PathMethods.Accessible:
			return cls.accessible_name(types, alias_handler)
		else:
			return cls.domain_name(types, alias_handler)

	@classmethod
	def __namespace(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの名前空間を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 名前空間
		"""
		if not alias_handler:
			return DSN.shift(DSN.relativefy(types.namespace, types.module_path), -1)

		return DSN.join(*[cls.domain_name(ancestor, alias_handler) for ancestor in cls.__ancestor_classes(types)])

	@classmethod
	def __ancestor_classes(cls, types: defs.ClassDef) -> list[defs.ClassDef]:
		"""名前空間を持つ親クラスを再帰的に抽出

		Args:
			types (ClassDef): 起点のクラス宣言ノード
		Returns:
			list[ClassDef]: 親クラスのノードリスト
		Note:
			FIXME 設計的にはIScopeを判断材料とするべき
		"""
		curr = types.parent
		ancestors: list[defs.ClassDef] = []
		while not isinstance(curr, defs.Entrypoint):
			if isinstance(curr, defs.ClassDef):
				ancestors.append(curr)

			curr = curr.parent

		return ancestors


class ClassShorthandNaming:
	"""クラスの短縮表記生成モジュール

	Note:
		# 書式
		* types=AltClass: ${alias}=${actual}
		* types=Function: ${domain_name}(...${arguments}) -> ${return}
		* その他: ${domain_name}<...${attributes}>
	"""

	@classmethod
	def domain_name(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(ドメイン名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, PathMethods.Domain)

	@classmethod
	def fullyname(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(完全参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, PathMethods.Fully)

	@classmethod
	def accessible_name(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(名前空間上の参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, PathMethods.Accessible)

	@classmethod
	def domain_name_for_debug(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(ドメイン名/デバッグ用)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, PathMethods.Domain, omit_attrs=[])

	@classmethod
	def __make_impl(cls, raw: IReflection, alias_handler: AliasHandler | None, path_method: PathMethods, omit_attrs: list[type[Node]] = [defs.AltClass]) -> str:
		"""クラスの短縮表記を生成

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー
			path_method (PathMethods): パス生成方式
			omit_attrs (list[type[Node]]): 拡張情報の省略対象 (default = [AltClass])
		Returns:
			str: 短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, alias_handler, path_method)
		adding_attrs = len(omit_attrs) == 0 or not issubclass(type(raw.types), *omit_attrs)
		if adding_attrs and len(raw.attrs) > 0:
			if raw.types.is_a(defs.AltClass):
				attrs = [cls.__make_impl(attr, alias_handler, path_method, omit_attrs) for attr in raw.attrs]
				return f'{symbol_name}={attrs[0]}'
			elif raw.types.is_a(defs.Function):
				attrs = [cls.__make_impl(attr, alias_handler, path_method, omit_attrs) for attr in raw.attrs]
				return f'{symbol_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
			else:
				attrs = [cls.__make_impl(attr, alias_handler, path_method, omit_attrs) for attr in raw.attrs]
				return f'{symbol_name}<{", ".join(attrs)}>'

		return symbol_name
