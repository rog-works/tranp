from typing import Protocol

from rogw.tranp.semantics.reflection.interface import IReflection, Roles
from rogw.tranp.syntax.ast.dsn import DSN
import rogw.tranp.syntax.node.definition as defs


class AliasHandler(Protocol):
	"""エイリアス解決ハンドラープロトコル"""

	def __call__(self, key: str, fallback: str = '') -> str:
		"""キーに対応する文字列に変換

		Args:
			key (str): エイリアスキー
			fallback (str): 存在しない場合の代用値(default = '')
		Returns:
			str: エイリアス
		Note:
			@see i18n.I18n.t
		"""
		...


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
		Note:
			# エイリアスの解決時に要求するキー名の書式
			'aliases.${fullyname}'
		"""
		return alias_handler(DSN.join('aliases', types.fullyname), fallback=types.domain_name) if alias_handler else types.domain_name

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
	def make_manualy(cls, types: defs.ClassDef, alias_handler: AliasHandler | None = None, path_method: str = 'domain') -> str:
		"""クラスのドメイン名を生成

		Args:
			types (ClassDef): クラス宣言ノード
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
			path_method ('domain' | 'fully' | 'namespace'): パス生成方式 (default = 'domain')
		Returns:
			str: ドメイン名
		"""
		if path_method == 'fully':
			return cls.fullyname(types, alias_handler)
		if path_method == 'accessible':
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

		return DSN.join(*[cls.domain_name(ancestor, alias_handler) for ancestor in types.ancestor_classes()])


class ClassShorthandNaming:
	"""クラスの短縮表記生成モジュール

	Note:
		# 書式
		* types=AltClass: ${alias}=${actual}
		* types=Function: ${domain_name}(...${arguments}) -> ${return}
		* role=Var/Generic/Literal/Reference: ${domain_name}<...${attributes}>
		* その他: ${domain_name}
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
		return cls.__make_impl(raw, alias_handler, 'domain')

	@classmethod
	def fullyname(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(完全参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, 'fully')

	@classmethod
	def accessible_name(cls, raw: IReflection, alias_handler: AliasHandler | None = None) -> str:
		"""クラスの短縮表記を生成(名前空間上の参照名)

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
		Returns:
			str: 短縮表記
		"""
		return cls.__make_impl(raw, alias_handler, 'accessible')

	@classmethod
	def __make_impl(cls, raw: IReflection, alias_handler: AliasHandler | None = None, path_method: str = 'domain') -> str:
		"""クラスの短縮表記を生成

		Args:
			raw (IReflection): シンボル
			alias_handler (AliasHandler | None): エイリアス解決ハンドラー (default = None)
			path_method ('domain' | 'fully' | 'namespace'): パス生成方式 (default = 'domain') @see analyze.naming.ClassDomainNaming
		Returns:
			str: 短縮表記
		"""
		symbol_name = ClassDomainNaming.make_manualy(raw.types, alias_handler, path_method)
		if len(raw.attrs) > 0:
			if raw.types.is_a(defs.AltClass):
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}={attrs[0]}'
			elif raw.types.is_a(defs.Function):
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}({", ".join(attrs[:-1])}) -> {attrs[-1]}'
			else:
				attrs = [cls.__make_impl(attr, alias_handler, path_method) for attr in raw.attrs]
				return f'{symbol_name}<{", ".join(attrs)}>'

		return symbol_name
