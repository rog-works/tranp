class IScope:
	"""スコープインターフェイス

	Note:
		対象: クラス/ファンクション/フロー構文/リスト内包表記
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
		対象: 名前宣言/変数参照/リテラル(コレクション以外)/フロー構文(pass/break/continue)/インポート/終端記号
	"""
	pass


class IDomain:
	"""ドメインインターフェイス

	Note:
		対象: クラス/ファンクション/シンボル/リテラル
	"""
	pass
