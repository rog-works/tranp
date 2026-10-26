from typing import Annotated

from example.material.me import ME
from example.material.me_types import float2
from example.material.mfs_02_math import math_010, math_aspect2d, math_atan2_clock


def uv_invert_x(uv: Annotated[float2, ME.tex_coord(0)], border: Annotated[float, 1.0]) -> float2:
	"""UV座標の進行逆転 (X軸)

	Args:
		uv: UV座標
		border: 逆転境界 (0 < n <= 1)
	Returns:
		UV座標
	"""
	x = math_010(uv.x, border * 2.0) * border
	return float2(x, uv.y)


def uv_to_vector(uv: Annotated[float2, ME.tex_coord(0)]) -> float2:
	"""UV座標からベクトルに変換

	Args:
		uv: UV座標
	Returns:
		ベクトル (-1 ~ 1)
	"""
	return uv * 2.0 - 1.0


def uv_to_resolution(uv: Annotated[float2, ME.tex_coord(0)], dpi_scale: Annotated[float, 0.666]) -> float2:
	"""UV座標から解像度を算出

	Args:
		uv: UV座標
		dpi_scale: DPIスケール (default = 0.666)
	Returns:
		解像度
	Note:
		UMGエディター確認用。デバッグ用途
	"""
	dx = ME.ddx(uv)
	dy = ME.ddy(uv)
	aspect = ME.abs(dx).length() / ME.abs(dy).length()
	ax = ME.min(1.0, aspect)
	ay = ME.max(1.0, aspect)
	pixel_size = (dx.length() / ax) + (dy.length() * ay)
	# 最終結果を2倍すると期待する結果と一致する(DDX/DDYでは半径を元に計算している？)
	resolution = (1.0 / math_aspect2d(aspect)) * (1.0 / pixel_size) * 2.0
	return resolution * (1.0 / dpi_scale)


def uv_deformation(uv: Annotated[float2, ME.tex_coord(0)], offset: Annotated[float2, float2(0.0, 0.0)], aspect: Annotated[float, 1.0], scale: Annotated[float2, float2(1.0, 1.0)]) -> float2:
	"""UV座標の変形

	Args:
		uv: UV座標
		offset: オフセット座標 (default = 0:0)
		aspect: アスペクト比 (default = 1.0)
		scale: 拡大率 (0以上, default = 1.0)
	Returns:
		変形後のUV座標
	"""
	deform = float2(1.0, 1.0) / (math_aspect2d(aspect) * scale)
	half = (float2(1.0, 1.0) - deform) * 0.5
	return (uv + offset) * deform + half


def uv_radial(uv: Annotated[float2, ME.tex_coord(0)], offset: Annotated[float2, float2(0.0, 0.0)], scale: Annotated[float, 1.0]) -> float2:
	"""UV座標リマッピング(放射状)

	Args:
		uv: UV座標
		offset: オフセット座標 (default = 0:0)
		scale: 倍率 (default = 1.0)
	Returns:
		UV座標
	"""
	scale_multi = 1.0 / scale
	scale_offset = (scale_multi - 1.0) * 0.5
	deform = (uv + offset) * scale_multi - scale_offset
	vector = uv_to_vector(deform)
	ux = math_atan2_clock(vector.y, vector.x)
	uy = vector.length()
	return float2(ux, uy)
