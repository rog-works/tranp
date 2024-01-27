class IScope:
	"""スコープインターフェイス

	Note:
		対象: クラス/ファンクション/ブロック
	"""

	@property
	def scope_part(self) -> str:
		"""str: スコープパート名 Note: 実装対象以外は空文字。対象: クラス/ファンクション/ブロック"""
		raise NotImplementedError()

	@property
	def namespace_part(self) -> str:
		"""str: 名前空間パート名 Note: 実装対象以外は空文字。対象: クラス"""
		raise NotImplementedError()


class ITerminal:
	"""終端要素インターフェイス。配下の要素の展開可否を扱う。終端記号とは別の概念である点に注意

	Note:
		対象: シンボル/リテラル/インポート/終端記号
	"""
	pass


class IDomainName:
	"""ドメイン名インターフェイス

	Note:
		対象: クラス/ファンクション/シンボル/リテラル
	"""

	@property
	def domain_name(self) -> str:
		"""str: ドメイン名 Note: スコープを除いた参照名"""
		raise NotImplementedError()

	@property
	def fullyname(self) -> str:
		"""str: 完全参照名 Note: スコープとドメイン名を合わせた参照名"""
		raise NotImplementedError()
