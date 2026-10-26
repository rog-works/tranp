from typing import Annotated

from example.material.me import ME
from example.material.me_types import float2
from example.material.mfs_00_preview import preview_alpha, preview_distance, preview_vector


def math_resolution_to_aspect(resolution: Annotated[float2, float2(250.0, 250.0)]) -> float:
	"""解像度からアスペクト比を算出

	Args:
		resolution: 解像度 (default = 250:250)
	Returns:
		アスペクト比
	"""
	return resolution.y / resolution.x


def math_resolution_to_pixel_size(resolution: Annotated[float2, float2(250.0, 250.0)]) -> float:
	"""解像度からピクセルサイズを算出

	Args:
		resolution: 解像度 (default = 250:250)
	Returns:
		ピクセルサイズ
	Note:
		常に小さい方を返却(タイリング前提)
	"""
	return 1.0 / ME.min(resolution.x, resolution.y)


def math_aspect2d(aspect: Annotated[float, 1.0]) -> float2:
	"""アスペクト比(2次元)を生成

	Args:
		aspect: アスペクト比
	Returns:
		アスペクト比(2次元)
	Note:
		```
		aspect=1.0: 1.0:1.0 (同じ)
		aspect=0.5: 0.5:1.0 (X軸が2倍)
		aspect=1.5: 1.0:0.5 (Y軸が2倍)
		```
	"""
	return float2(ME.min(1.0, aspect), ME.min(1.0, 1.0 / aspect))


def math_atan2_clock(y: Annotated[float, 0.0], x: Annotated[float, preview_alpha(1.0)]) -> float:
	"""Arctangent2Fast。0時を始点に時計周りに1周の割合(0 ~ 1)を返す

	Args:
		y: Y座標
		x: X座標
	Returns:
		1周の割合 (0 ~ 1)
	Note:
		```
		XXX (0, 0)の時に180度になる不具合が存在
		XXX しかし大抵は問題にならず、回避するための計算コスト増加の方が問題として大きいため、許容することにする
		```
	"""
	return ME.atan2_fast(-x, y) / (2.0 * ME.pi()) + 0.5


def math_calc_location(u_theta: Annotated[float, preview_distance()], length: Annotated[float, 1.0]) -> float2:
	"""0時を始点に角度と長さを基に座標を算出

	Args:
		u_theta: 1周の割合 (0 ~ 1)
		length: 長さ (default = 1.0)
	Returns:
		座標
	"""
	return float2(ME.sin(u_theta), -ME.cos(u_theta)) * length


def math_101(value: Annotated[float, preview_distance()], unit: Annotated[float, 1.0]) -> float:
	"""単位の中央値を境に反転した値を返す (1 ~ 0 ~ 1)

	Args:
		value: 値
		unit: 単位 (default = 1.0)
	Returns:
		1 ~ 0 ~ 1
	"""
	half = unit * 0.5
	return ME.abs((value - half) / half)


def math_101_flex(value: Annotated[float, preview_distance()], unit: Annotated[float, 1.0], center: Annotated[float, 0.5]) -> float:
	"""指定の中央値を境に反転した値を返す (1 ~ 0 ~ 1)

	Args:
		value: 値
		unit: 単位 (default = 1.0)
		center: 中央値 (default = 0.5)
	Returns:
		1 ~ 0 ~ 1
	"""
	remain = unit - center
	abs_value = ME.abs(value - center)
	sign = float(value <= center)
	left = abs_value / ME.max(0.0001, center) * sign
	right = abs_value / ME.max(0.0001, remain) * float(not sign)
	return left + right


def math_010(value: Annotated[float, preview_distance()], unit: Annotated[float, 1.0]) -> float:
	"""単位の中央値を境に反転した値を返す (0 ~ 1 ~ 0)

	Args:
		value: 値
		unit: 単位 (default = 1.0)
	Returns:
		0 ~ 1 ~ 0
	"""
	return 1.0 - math_101(value, unit)


def math_linear_edge(value: Annotated[float, preview_distance()], maximum: Annotated[float, 1.0], threshold: Annotated[float, 0.1]) -> float:
	"""範囲の先端と終端から閾値の範囲内に値が存在する場合、0 ~ 1まで線形補完で返す

	Args:
		value: 値
		maximum: 範囲
		threshold: 閾値
	Returns:
		0 ~ 1
	"""
	half = maximum * 0.5
	half_section = ME.abs(value % maximum - half)
	diff = half_section - (half - threshold)
	return ME.saturate(diff) / threshold


def math_vector_to_edge(vector: Annotated[float2, preview_vector()]) -> float:
	"""ベクトルから角方向に変換

	Args:
		vector: ベクトル
	Returns:
		方向(1=左上, 2=右上, 3=左下, 4=右下)
	"""
	minus_x = float(vector.x < 0.0)
	minus_y = float(vector.y < 0.0)
	plus_x = float(not minus_x)
	plus_y = float(not minus_y)
	lt = minus_x * minus_y
	rt = plus_x * minus_y * 2.0
	lb = minus_x * plus_y * 3.0
	rb = plus_x * plus_y * 4.0
	return lt + rt + lb + rb
