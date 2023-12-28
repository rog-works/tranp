class ScopeTrait:
	"""スコープを所有するノードを明示

	Note:
		対象: ブロック/仮引数/戻り値
	"""


class TerminalTrait:
	"""終端要素のノードを明示

	Note:
		対象: シンボル/一部のリテラル(int/float/str/bool/None)
	"""


class DomainNameTrait:
	"""ドメイン名で解決出来るノードを明示

	Note:
		対象: クラス/関数/シンボル/リテラル
	"""

	@property
	def domain_id(self) -> str:
		raise NotImplementedError()

	@property
	def domain_name(self) -> str:
		raise NotImplementedError()
