class DSN:
	"""ドメイン特化名操作ユーティリティー"""

	@classmethod
	def elem_counts(cls, origin: str, delimiter: str = '.') -> int:
		"""ドメイン名内の要素数を取得

		Args:
			origin: ドメイン名
			delimiter: デリミター(default = '.')
		Returns:
			要素数
		"""
		return 0 if origin == '' else origin.count(delimiter) + (0 if origin.startswith(delimiter) else 1)

	@classmethod
	def elements(cls, origin: str, delimiter: str = '.') -> list[str]:
		"""ドメイン名を要素に分解

		Args:
			origin: ドメイン名
			delimiter: デリミター(default = '.')
		Returns:
			要素リスト
		"""
		return [elem for elem in origin.split(delimiter) if elem]

	@classmethod
	def join(cls, *parts: str, delimiter: str = '.') -> str:
		"""ドメイン名の要素を結合。空の要素は除外される

		Args:
			*parts (str): 要素リスト
			delimiter: デリミター(default = '.')
		Returns:
			ドメイン名
		"""
		return delimiter.join([part for part in parts if part])

	@classmethod
	def left(cls, origin: str, counts: int, delimiter: str = '.') -> str:
		"""左から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin: ドメイン名
			counts: 要素数
			delimiter: デリミター(default = '.')
		Returns:
			ドメイン名
		"""
		return cls.join(*(cls.elements(origin, delimiter)[0:counts]), delimiter=delimiter)

	@classmethod
	def right(cls, origin: str, counts: int, delimiter: str = '.') -> str:
		"""右から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin: ドメイン名
			counts: 要素数
			delimiter: デリミター(default = '.')
		Returns:
			ドメイン名
		"""
		return cls.join(*(cls.elements(origin, delimiter)[-counts:]), delimiter=delimiter)

	@classmethod
	def shift(cls, origin: str, skip: int, delimiter: str = '.') -> str:
		"""指定方向分要素を除外しドメイン名を生成

		Args:
			origin: ドメイン名
			skip: 移動方向
			delimiter: デリミター(default = '.')
		Returns:
			ドメイン名
		"""
		elems = cls.elements(origin, delimiter)
		if skip == 0:
			pass
		elif skip > 0:
			elems = elems[skip:]
		elif skip < 1:
			elems = elems[:skip]

		return cls.join(*elems, delimiter=delimiter)

	@classmethod
	def root(cls, origin: str, delimiter: str = '.') -> str:
		"""ルート要素を取得

		Args:
			origin: ドメイン名
			delimiter: デリミター(default = '.')
		Returns:
			ルート要素
		"""
		return cls.elements(origin, delimiter)[0]

	@classmethod
	def parent(cls, origin: str, delimiter: str = '.') -> str:
		"""親の要素を取得

		Args:
			origin: ドメイン名
			delimiter: デリミター(default = '.')
		Returns:
			親の要素
		"""
		return cls.elements(origin, delimiter)[-2]

	@classmethod
	def relativefy(cls, origin: str, starts: str, delimiter = '.') -> str:
		"""指定のパスより先の相対パスを生成

		Args:
			starts: 先頭のパス
		Returns:
			相対パス
		"""
		if starts != origin and not origin.startswith(f'{starts}{delimiter}'):
			return origin

		elems = [elem for elem in origin.split(starts)[1].split(delimiter)]
		return cls.join(*elems)
