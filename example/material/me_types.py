from enum import Enum
from typing import Self, overload

from numpy import cross as np_cross
from numpy import dot as np_dot
from numpy import linalg as np_linalg
from numpy import sqrt as np_sqrt

EqualThreshold = 0.001


class SamplerTypes(Enum):
	"""テクスチャーサンプル種別"""
	Color = 'Color'
	Grayscale = 'LinearGrayscale'
	Linear = 'LinearColor'


class _Vector:
	"""ベクトル(基底)"""

	elems: list[float]

	def __init__(self, *elems: float) -> None:
		"""インスタンスを生成

		Args:
			elems: 要素リスト
		Raises:
			ValueError: 要素数が0
		"""
		if not elems:
			raise ValueError(self)

		self.elems = list(elems)

	@property
	def x(self) -> float:
		"""Returns: X"""
		return self.elems[0]

	@property
	def y(self) -> float:
		"""Returns: Y"""
		return self.elems[1]

	def length(self) -> float:
		"""Returns: ベクトルの長さ """
		return float(np_sqrt(sum([elem * elem for elem in self.elems])))

	def normalize(self: Self) -> Self:
		"""Returns: 単位ベクトル """
		# FIXME マテリアル関数の仕組み上、演算を除外することが不可能なためゼロ除算対策をする
		if len([elem for elem in self.elems if elem > 0.0]) == 0:
			return self.__class__(*[0.0001 for _ in range(len(self.elems))])

		return self / float(np_linalg.norm(self.elems))

	def dot(self: Self, other: Self) -> float:
		"""Args: other: ベクトル Returns: 内積"""
		return float(np_dot(self.elems, other.elems))

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: {str(self)}>'

	def __str__(self) -> str:
		"""Returns: 文字列表現"""
		return f'({", ".join(map(str, self.elems))})'
	
	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return hash(self.elems)
	
	def __eq__(self: Self, other: Self | float) -> bool:
		"""比較(一致) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return len([True for elem in self.elems if abs(elem - other) <= EqualThreshold]) == len(self.elems)
		elif isinstance(other, _Vector) and type(self) == type(other):
			return len([True for index in range(len(self.elems)) if abs(self.elems[index] - other.elems[index]) <= EqualThreshold]) == len(self.elems)
		else:
			raise ValueError(self, other)

	def __ne__(self: Self, other: Self | float) -> bool:
		"""比較(不一致) Args: other: 値 Returns: 結果"""
		return not self.__eq__(other)

	def __add__(self: Self, other: Self | float) -> Self:
		"""算術演算(加算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[elem + other for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[self.elems[index] + other.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)

	def __sub__(self: Self, other: Self | float) -> Self:
		"""算術演算(減算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[elem - other for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[self.elems[index] - other.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)

	def __mul__(self: Self, other: Self | float) -> Self:
		"""算術演算(乗算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[elem * other for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[self.elems[index] * other.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)

	def __truediv__(self: Self, other: Self | float) -> Self:
		"""算術演算(除算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[elem / other for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[self.elems[index] / other.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)

	def __rtruediv__(self: Self, other: Self | float) -> Self:
		"""算術演算(除算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[other / elem for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[other.elems[index] / self.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)

	def __mod__(self: Self, other: Self | float) -> Self:
		"""算術演算(余算) Args: other: 値 Returns: 結果"""
		if isinstance(other, float):
			return self.__class__(*[elem % other for elem in self.elems])
		elif isinstance(other, _Vector) and type(self) == type(other):
			return self.__class__(*[self.elems[index] % other.elems[index] for index in range(len(self.elems))])
		else:
			raise ValueError(self, other)


class float2(_Vector):
	"""ベクトル(2次元)"""

	def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
		"""インスタンスを生成

		Args:
			x: X (default = 0.0)
			y: Y (default = 0.0)
		"""
		super().__init__(x, y)

	def append(self, elem: float) -> 'float3':
		""" Args: elem: 追加する要素 Returns: ベクトル(3次元)"""
		return float3(self.x, self.y, elem)


class float3(_Vector):
	"""ベクトル(3次元)"""

	@overload
	def __init__(self) -> None:
		"""インスタンスを生成"""
		...

	@overload
	def __init__(self, x: float, y: float, z: float) -> None:
		"""インスタンスを生成

		Args:
			x: X
			y: Y
			z: Z
		"""
		...

	@overload
	def __init__(self, code: int) -> None:
		"""インスタンスを生成

		Args:
			code: カラーコード(RRGGBBAA)
		"""
		...

	def __init__(self, *args: int | float, **kwargs: int | float) -> None:
		"""インスタンスを生成 @see overload"""
		if len(args) == 1 and isinstance(args[0], int):
			code = args[0]
			r = (code >> 24) & 0xff
			g = (code >> 16) & 0xff
			b = (code >> 8) & 0xff
			super().__init__(r / 255.0, g / 255.0, b / 255.0)
		elif len(args) == 3 and isinstance(args[0], float) and isinstance(args[1], float) and isinstance(args[2], float):
			super().__init__(args[0], args[1], args[2])
		else:
			super().__init__()

	@property
	def z(self) -> float:
		"""Returns: Z"""
		return self.elems[2]

	@property
	def xy(self) -> float2:
		"""Returns: XY"""
		return float2(self.x, self.y)

	def append(self, elem: float) -> 'float4':
		""" Args: elem: 追加する要素 Returns: ベクトル(4次元)"""
		return float4(self.x, self.y, self.z, elem)

	def cross(self, other: 'float3') -> 'float3':
		"""Args: other: ベクトル Returns: 外積"""
		return float3(*[float(e) for e in np_cross(self.elems, other.elems)])


class float4(_Vector):
	"""ベクトル(4次元)"""

	def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0) -> None:
		"""インスタンスを生成

		Args:
			x: X (default = 0.0)
			y: Y (default = 0.0)
			z: Z (default = 0.0)
			w: W (default = 0.0)
		"""
		super().__init__(x, y, z, w)

	@property
	def z(self) -> float:
		"""Returns: Z"""
		return self.elems[2]

	@property
	def w(self) -> float:
		"""Returns: W"""
		return self.elems[3]

	@property
	def xy(self) -> float2:
		"""Returns: XY"""
		return float2(self.x, self.y)

	@property
	def xyz(self) -> float3:
		"""Returns: XYZ"""
		return float3(self.x, self.y, self.z)


class texture:
	"""テクスチャー"""

	src: str

	def __init__(self, src: str, sampler: str = SamplerTypes.Color.value) -> None:
		"""インスタンスを生成

		Args:
			src: テクスチャーソースパス
			sampler: テクスチャーサンプル種別
		"""
		self.src = src

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: "{self.src}">'
