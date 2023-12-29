class DSN:
	"""AST用のドメイン名ユーティリティー。ドット区切りで要素を結合した書式を前提とする"""

	@classmethod
	def length(cls, origin: str) -> int:
		"""ドメイン名内の要素数を取得

		Args:
			origin (str): ドメイン名
		Returns:
			int: 要素数
		"""
		return len(origin.split('.'))

	@classmethod
	def join(cls, domain: str, *prats: str) -> str:
		"""ドメイン名の要素を結合。空の要素は除外される

		Args:
			domain (str): 基点
			*parts (str): 要素リスト
		Returns:
			str: ドメイン名
		"""
		return '.'.join([domain, *[part for part in prats if part]])

	@classmethod
	def left(cls, origin: str, counts: int) -> str:
		"""左から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin (str): ドメイン名
			counts (int): 要素数
		Returns:
			str: ドメイン名
		"""
		return cls.join(*origin.split('.')[0:counts])

	@classmethod
	def right(cls, origin: str, counts: int) -> str:
		"""右から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin (str): ドメイン名
			counts (int): 要素数
		Returns:
			str: ドメイン名
		"""
		return cls.join(*origin.split('.')[-counts:])
