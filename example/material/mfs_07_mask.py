from typing import Annotated

from example.material.me import ME
from example.material.me_types import float2, texture
from example.material.mf_const import MFImages
from example.material.mfs_00_preview import preview_alpha, preview_distance, preview_vector
from example.material.mfs_01_op import op_bit4_on
from example.material.mfs_02_math import math_101_flex, math_aspect2d, math_atan2_clock, math_calc_location, math_linear_edge, math_vector_to_edge
from example.material.mfs_06_uv import uv_to_vector


def mask_polygon(vector: Annotated[float2, preview_vector()], sides: Annotated[float, 3.0]) -> float:
	"""多角形マスクを生成

	Args:
		vector: ベクトル
		sides: 角の数 (3 ~ 10, default = 3.0)
	Returns:
		強度
	"""
	in_sides = ME.floor(ME.max(3.0, sides))

	# ベクトルの角度を算出
	u_vector = ME.atan2_fast(vector.x, vector.y) / (2.0 * ME.pi())
	# 1単位(=面)ごとの目標の角度を算出。360度/角数=1単位なので、0.5単位加算することで区分を半単位ずらす
	u_max = 1.0 / in_sides
	u_face = ME.floor(u_vector / u_max + 0.5) * u_max

	# ベクトルの単位長を算出。誤差が0.5単位の時、1の長さになる
	u_half = u_max * 0.5
	unit_vector = vector / ME.cos(u_half)
	v_length = unit_vector.length()
	# 目標の角度との誤差を算出。中央反転するため誤差は-0.5~0.5単位になる
	u_diff = u_face - u_vector
	# ベクトルの距離を算出。角の角度に近いほど(=誤差が小さい)長くなる
	return ME.cos(u_diff) * v_length


def mask_polygon_round(vector: Annotated[float2, preview_vector()], sides: Annotated[float, 3.0], round_r: Annotated[float, 0.1]) -> float:
	"""多角形マスクを生成(角丸)

	Args:
		vector: ベクトル
		sides: 角の数 (3 ~ 10, default = 3.0)
		round_r: 角丸の半径 (0 < n < 1, default = 0.1)
	Returns:
		強度
	"""
	t_360 = 2.0 * ME.pi()
	u_max = 1.0 / sides
	u_half = u_max * 0.5

	# 初期位置の向きを合わせるため半単位引き、鏡像反転するため絶対値を取る
	u_theta = ME.abs(ME.atan2_fast(vector.x, vector.y) / t_360 - u_half)

	# 多角形の1面を半分にした2等辺三角形の各辺の距離を算出
	t0 = 0.5 - (0.25 + u_half)
	b0 = 1.0
	h0 = ME.dot(b0, ME.sin(t0))

	# 角丸の半径の交点から多角形先端部の各辺の距離を算出
	h1 = round_r * (1.0 / float2(1.0, 1.0).length())
	a1 = h1 / ME.tan(t0)

	# 角丸の有効角度(t2)を算出
	b2 = b0 - a1
	t2 = ME.atan2_fast(h1, b2) / t_360

	# ベクトルの角度における多角形の境界線までの長さ(b3)を算出
	t3 = ME.abs(u_theta % u_max - u_half)
	h3 = ME.dot(h0, ME.tan(t3))
	b3 = float2(h3, h0).length()

	# 角丸の有効角度から(0 ~ 1)を算出
	alpha = math_linear_edge(u_theta, u_max, t2)

	# 角丸の座標を算出
	round_t = (0.5 + 0.5 * alpha) * 0.25
	round = float2(ME.cos(round_t), ME.sin(round_t)) * round_r
	round_base = float2(0.0, b0 - (a1 + h1))
	round_pos = round + round_base
	round_l = round_pos.length()

	# ベクトルの距離を基に境界線までの割合を算出
	return vector.length() / ME.min(b3, round_l)


def mask_square(vector: Annotated[float2, preview_vector()], size: Annotated[float, 1.0]) -> float:
	"""四角マスクを生成

	Args:
		vector: ベクトル
		size: 径 (0 ~ 1, default = 1.0)
	Returns:
		強度
	"""
	abs_vector = ME.abs(vector)
	return ME.max(abs_vector.x, abs_vector.y) / size


def mask_square_round(vector: Annotated[float2, preview_vector()], size: Annotated[float, 1.0], radius: Annotated[float, 0.5], radius_min: Annotated[float, 0.0], allows: Annotated[float, 15.0]) -> float:
	"""四角マスク(角丸)を生成

	Args:
		vector: ベクトル
		size: 径 (0 ~ 1, default = 1.0)
		radius: 角丸の半径 (0 < n < size, default = 0.5)
		radius_min: 角丸の半径/下限 (n < radius < size, default = 0.0)
		allows: 角丸生成ビットフラグ (0 ~ 15, default = 15)
	Returns:
		強度
	"""
	allow = op_bit4_on(allows, math_vector_to_edge(vector))
	# 正規ベクトルから1の斜辺の最大長を算出。中心点(0, 0)はゼロ除算が発生するため対策
	nv = ME.abs(vector).normalize()
	max_y = ME.min(nv.x, nv.y) / ME.max(0.001, ME.max(nv.x, nv.y))
	max_length = float2(1.0, ME.saturate(max_y)).length()
	# 半径内のY座標から0 ~ 1を算出。半径の円の長さから減算量を算出
	clamp_radius = ME.max(radius * allow, radius_min)
	radius_y = ME.max(max_y - (1.0 - clamp_radius), 0.0) / ME.max(0.001, clamp_radius)
	radius_length = float2(clamp_radius, radius_y * clamp_radius).length()
	diff_length = radius_length - clamp_radius
	# 角丸時の最大長と最大長の比率を基にサイズを補正
	round_length = max_length - diff_length
	clamp_size = size * max_length * (round_length / max_length)
	return vector.length() / clamp_size


def mask_square_round_fix(uv: Annotated[float2, ME.tex_coord(0)], aspect: Annotated[float, 1.0], radius: Annotated[float, 0.5], radius_min: Annotated[float, 0.0], allows: Annotated[float, 15.0]) -> float:
	"""四角マスク(角丸/アスペクト比固定)を生成

	Args:
		uv: UV座標
		aspect: アスペクト比
		radius: 角丸の半径 (0 < n < size, default = 0.5)
		radius_min: 角丸の半径/下限 (n < radius < size, default = 0.0)
		allows: 角丸生成ビットフラグ (0 ~ 15, default = 15)
	Returns:
		強度
	"""
	aspect2d = math_aspect2d(aspect)
	half = ME.min(aspect2d.x, aspect2d.y) * 0.5
	long_x = float(aspect < 1.0)
	long_y = float(not long_x)
	v = uv.x * long_x + uv.y * long_y
	boundary = 1.0 - half
	on_end = float(v > boundary)
	on_begin = float(not on_end)
	v_begin = ME.min(0.5 * v / half, 0.5)
	v_end = 0.5 + (0.5 * (v - boundary) / half)
	v0 = v_begin * on_begin + v_end * on_end
	x = v0 * long_x + uv.x * long_y
	y = uv.y * long_x + v0 * long_y
	return mask_square_round(uv_to_vector(float2(x, y)), 1.0, radius, radius_min, allows)


def mask_rect(vector: Annotated[float2, preview_vector()], end: Annotated[float2, float2(0.5, 0.5)], center: Annotated[float2, float2(0.0, 0.0)]) -> float:
	"""矩形マスクを生成

	Args:
		vector: ベクトル
		end: マスク終了座標 (0以上)
		center: 中心座標 (0 ~ 1, default = 0:0)
	Returns:
		マスク
	"""
	in_vector = ME.abs(vector - center)
	return float(in_vector.x <= end.x) * float(in_vector.y <= end.y)


def mask_rect_edge(vector: Annotated[float2, preview_vector()], start: Annotated[float2, float2(0.5, 0.5)], center: Annotated[float2, float2(0.0, 0.0)]) -> float:
	"""四隅の矩形マスクを生成

	Args:
		vector: ベクトル
		start: マスク開始座標 (0以上)
		center: 中心座標 (0 ~ 1, default = 0:0)
	Returns:
		マスク
	"""
	in_vector = ME.abs(vector - center)
	return float(in_vector.x >= start.x) * float(in_vector.y >= start.y)


def mask_linear(distance: Annotated[float, preview_distance()], size: Annotated[float, 1.0]) -> float:
	"""線形(円)マスクを生成

	Args:
		distance: 距離 (0 ~ 1)
		size: 径 (0 ~ 1, default = 1.0)
	Returns:
		強度
	"""
	return distance / size


def mask_linear_range(distance: Annotated[float, preview_distance()], outer: Annotated[float, 1.0], size: Annotated[float, 0.5], center: Annotated[float, 0.5] = 0.5) -> float:
	"""線形(円/中抜き)マスクを生成

	Args:
		distance: 距離 (0 ~ 1)
		outer: 外径 (内径 <= 1)
		size: 線の径 (0 < n < 外径)
		center: 中心点 (0 ~ 1, default = 0.5)
	Returns:
		強度
	"""
	inner = ME.saturate(outer - size)
	diff = distance - inner
	unit = outer - inner
	return math_101_flex(diff, unit, center * unit)


def mask_cupsule(vector: Annotated[float2, preview_vector()], radius: Annotated[float, 0.5], begin: Annotated[float, -1.0], end: Annotated[float, 1.0]) -> float:
	"""カプセルマスクを生成

	Args:
		vector: ベクトル
		radius: 半径 (0 < n <= 1)
		begin: 始点 (-1 <= n < end)
		end: 終点 (begin < n <= 1)
	Returns:
		強度
	"""
	center = float2(ME.clamp(vector.x, begin, end), 0.0)
	return (vector - center).length() / radius


def mask_dissolve(alpha: Annotated[float, preview_alpha(0.5)], smooth: Annotated[float, 0.25], scroll: Annotated[float2, float2(0.1, 0.1)]) -> tuple[float, float, float]:
	"""消失マスクを生成

	Args:
		alpha: 進捗 (0 ~ 1)
		smooth: 浸食の均し範囲 (0 ~ 1, default = 0.25)
		scroll: マスク画像のスクロール速度 (default = 0.1:0.1)
	Returns:
		(マスク, 浸食マスク, 浸食α値)
	"""
	intensity = ME.sample(texture(MFImages.Noise.value), ME.panner(ME.tex_coord(0), scroll)).x

	expand = alpha + ME.min(alpha, smooth)
	zero = float(alpha <= 0.0)

	mask = ME.max(1.0 - float(intensity <= alpha), zero)
	min_mask = ME.max(1.0 - float(intensity <= expand), zero)
	min_alpha = ME.max(ME.smoothstep(alpha, expand, intensity), zero)
	return mask, min_mask, min_alpha


def mask_clock(vector: Annotated[float2, preview_vector()], alpha: Annotated[float, 0.0], center: Annotated[float, 0.0] = 0.0) -> float:
	"""時計マスクを生成

	Args:
		vector: ベクトル
		alpha: 進捗 (0 ~ 1)
		center: 中心 (-0.5 ~ 0 ~ 0.5, default = 0.0)
	Returns:
		強度
	"""
	u_theta_org = math_atan2_clock(vector.y, vector.x)
	u_theta = (u_theta_org - center + 1.0) % 1.0
	available = float(alpha > 0.0)
	# XXX マスクの境界値より大きくするため1.1倍にする
	zero = float(not available) * 1.1
	intensity = u_theta / ME.max(0.001, alpha)
	return intensity * available + zero


def mask_clock_cupsule(vector: Annotated[float2, preview_vector()], radius: Annotated[float, 1.0], alpha: Annotated[float, 0.0], center: Annotated[float, 0.0] = 0.0) -> float:
	"""時計マスク(カプセル)を生成

	Args:
		vector: ベクトル
		radius: 半径 (0 < n < 1)
		alpha: 進捗 (0 ~ 1)
		center: 中心 (-0.5 ~ 0 ~ 0.5, default = 0.0)
	Returns:
		強度
	"""
	half_radius = radius * 0.5
	length = 1.0 - radius + half_radius
	begin_diff = math_calc_location(center, length) - vector
	end_diff = math_calc_location(center + alpha, length) - vector
	begin_intensity = begin_diff.length() / half_radius
	end_intensity = end_diff.length() / half_radius
	line_intensity = mask_linear_range(vector.length(), 1.0, radius)
	clock_mask = float(mask_clock(vector, alpha, center) <= 1.0)
	return line_intensity * clock_mask + ME.min(begin_intensity, end_intensity) * float(not clock_mask)


def mask_stripe(intensity: Annotated[float, preview_distance()], size: Annotated[float, 1.0]) -> float:
	"""縞マスクを生成

	Args:
		intensity: 強度 (0 ~ 1)
		size: 縞のサイズ (1=Sin波1周)
	Returns:
		強度
	"""
	return 1.0 + ME.sin(intensity / size)


def mask_square_side(vector: Annotated[float2, preview_vector()], size: Annotated[float, 0.5], allows: Annotated[float, 15.0]) -> float:
	"""四角辺マスクを生成

	Args:
		vector: ベクトル
		size: 辺のサイズ (1未満, default = 0.5)
		allows: 辺生成ビットフラグ (0 ~ 15, default = 15)
	Returns:
		マスク
	"""
	boundary = 1.0 - size
	l = float(vector.x <= -boundary) * op_bit4_on(allows, 1.0)
	t = float(vector.y <= -boundary) * op_bit4_on(allows, 2.0)
	r = float(vector.x >= boundary) * op_bit4_on(allows, 3.0)
	b = float(vector.y >= boundary) * op_bit4_on(allows, 4.0)
	return (l + t + r + b) >= 1.0
