class ScopeTrait:
	"""スコープを所有するノードを明示

	Note:
		対象: クラス/ファンクション/ブロック
	"""

	@property
	def scope_part(self) -> str:
		"""str: スコープパート名 Note: 実装対象以外は空文字。対象: クラス/ファンクション/ブロック"""
		return ''

	@property
	def namespace_part(self) -> str:
		"""str: 名前空間パート名 Note: 実装対象以外は空文字。対象: クラス"""
		return ''


class TerminalTrait:
	"""終端要素のノードを明示

	Note:
		これ以上展開が不要な要素であることを表す。終端要素と終端記号は別物。
		対象: シンボル/コレクション以外のリテラル(Integer/Float/String/Boolean/Null)
	"""


class DomainNameTrait:
	"""ドメイン名で解決出来るノードを明示

	Note:
		対象: クラス/ファンクション/シンボル/リテラル
	"""

	@property
	def domain_id(self) -> str:
		"""str: ドメインID Note: FQDN。スコープと対応"""
		raise NotImplementedError()

	@property
	def domain_name(self) -> str:
		"""str: ドメイン名 Note: 名前空間と対応"""
		raise NotImplementedError()
