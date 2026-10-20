from typing import Annotated

from example.material.me import ME
from example.material.me_types import float2


def preview_vector() -> float2:
	"""UV座標を基に2次元ベクトルを生成(プレビュー用)

	Returns:
		2次元ベクトル (-1 ~ 1)
	"""
	return ME.tex_coord(0) * 2.0 - 1.0


def preview_distance() -> float:
	"""UV座標を基に距離を生成(プレビュー用)

	Returns:
		距離
	"""
	return preview_vector().length()


def preview_alpha(speed: Annotated[float, 1.0]) -> float:
	"""α値を生成(プレビュー用)

	Args:
		speed: 速度 (default = 1.0)
	Returns:
		α値 (0 ~ 1)
	"""
	return (ME.time() * speed) % 1.0
