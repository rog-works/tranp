from typing import Annotated

from example.material.me import ME
from example.material.me_types import float3
from example.material.mfs_00_preview import preview_alpha, preview_distance


def color_to_srgb(color: Annotated[float3, float3(1.0, 0.5, 0.0)]) -> float3:
	"""sRGBに変換

	Args:
		color: 色
	Returns:
		sRGB
	"""
	return float3(ME.rgb_to_srgb(color.x), ME.rgb_to_srgb(color.y), ME.rgb_to_srgb(color.z))


def color_to_rgb(color: Annotated[float3, float3(1.0, 0.5, 0.0)]) -> float3:
	"""RGBに変換

	Args:
		color: 色
	Returns:
		RGB
	"""
	return float3(ME.srgb_to_rgb(color.x), ME.srgb_to_rgb(color.y), ME.srgb_to_rgb(color.z))


def color_blend_a(bg: Annotated[float, 0.5], fore: Annotated[float, 0.5]) -> float:
	"""アルファ合成

	Args:
		bg: 背景
		fore: 前景
	Returns:
		合成結果
	"""
	return fore + (bg * (1.0 - fore))


def color_gradation_to_srgb(a: Annotated[float3, float3(1.0, 0.0, 0.0)], b: Annotated[float3, float3(0.0, 1.0, 0.0)], alpha: Annotated[float, 0.5]) -> float3:
	"""2色合成

	Args:
		a: 色A
		b: 色B
		alpha: α値
	Returns:
		合成結果(sRGB)
	Note:
		@see color_gration
	"""
	return ME.lerp(color_to_srgb(a), color_to_srgb(b), alpha)


def color_gradation(a: Annotated[float3, float3(1.0, 0.0, 0.0)], b: Annotated[float3, float3(0.0, 1.0, 0.0)], alpha: Annotated[float, 0.5]) -> float3:
	"""2色合成

	Args:
		a: 色A
		b: 色B
		alpha: α値
	Returns:
		合成結果
	Note:
		```
		* 色をそのままlerpで合成すると、人間の感覚では中間色が退色(彩度が下がる)して見えるため、sRGBに変換してから合成することで退色を抑制する
		* sRGBに変換した色合成は数学的には正しくないため、あくまでも見た目の向上と言う目的でのみ利用すること
		```
	"""
	return color_to_rgb(color_gradation_to_srgb(a, b, alpha))


def color_gradation3(a: Annotated[float3, float3(0.0, 0.0, 0.0)], b: Annotated[float3, float3(1.0, 0.0, 0.0)], c: Annotated[float3, float3(1.0, 1.0, 1.0)], alpha: Annotated[float, 0.0]) -> float3:
	"""3色合成(A -> B -> C)

	Args:
		a: 色A
		b: 色B
		c: 色C
		alpha: α値
	Returns:
		合成結果
	Note:
		@see color_gration
	"""
	alpha0 = ME.min(0.5, alpha) * 2.0
	alpha1 = (ME.max(0.5, alpha) - 0.5) * 2.0
	ab_srgb = color_gradation_to_srgb(a, b, alpha0)
	c_srgb = color_to_srgb(c)
	return color_to_rgb(ME.lerp(ab_srgb, c_srgb, alpha1))


def color_gradation_ab_to_c(a: Annotated[float3, float3(0.0, 0.0, 0.0)], b: Annotated[float3, float3(1.0, 0.0, 0.0)], c: Annotated[float3, float3(1.0, 1.0, 1.0)], alpha_a_to_b: Annotated[float, 0.0], alpha_ab_to_c: Annotated[float, 0.0]) -> float3:
	"""2色合成(AB -> C)

	Args:
		a: 色A
		b: 色B
		c: 色C
		alpha_a_to_b: α値(A -> B)
		alpha_ab_to_c: α値(AB -> C)
	Returns:
		合成結果
	Note:
		@see color_gration
	"""
	ab_srgb = color_gradation_to_srgb(a, b, alpha_a_to_b)
	c_srgb = color_to_srgb(c)
	return color_to_rgb(ME.lerp(ab_srgb, c_srgb, alpha_ab_to_c))


def color_gradation_c_to_ab(a: Annotated[float3, float3(0.0, 0.0, 0.0)], b: Annotated[float3, float3(1.0, 0.0, 0.0)], c: Annotated[float3, float3(1.0, 1.0, 1.0)], alpha_a_to_b: Annotated[float, 0.0], alpha_ab_to_c: Annotated[float, 0.0]) -> float3:
	"""2色合成(C -> AB)

	Args:
		a: 色A
		b: 色B
		c: 色C
		alpha_a_to_b: α値(A -> B)
		alpha_ab_to_c: α値(AB -> C)
	Returns:
		合成結果
	Note:
		@see color_gration
	"""
	ab_srgb = color_gradation_to_srgb(a, b, alpha_a_to_b)
	c_srgb = color_to_srgb(c)
	return color_to_rgb(ME.lerp(c_srgb, ab_srgb, alpha_ab_to_c))


def color_gradation_line_ab_to_c(line_a: Annotated[float3, float3(0.0, 0.0, 0.0)], line_b: Annotated[float3, float3(1.0, 0.0, 0.0)], line_c: Annotated[float3, float3(1.0, 1.0, 1.0)], base: Annotated[float3, float3(1.0, 1.0, 1.0)], alpha_a_to_b: Annotated[float, 0.0], alpha_ab_to_c: Annotated[float, 0.0], alpha_base_to_line: Annotated[float, 0.0]) -> float3:
	"""2色合成(ベースカラー -> ラインカラー(AB -> C))

	Args:
		line_a: 色A
		line_b: 色B
		line_c: 色C
		base: ベースカラー
		alpha_a_to_b: α値(A -> B)
		alpha_ab_to_c: α値(AB -> C)
		alpha_base_to_line: α値(ベースカラー -> ラインカラー)
	Returns:
		合成結果
	Note:
		@see color_gration
	"""
	line_ab_srgb = color_gradation_to_srgb(line_a, line_b, alpha_a_to_b)
	line_c_srgb = color_to_srgb(line_c)
	line_srgb = ME.lerp(line_ab_srgb, line_c_srgb, alpha_ab_to_c)
	base_srgb = color_to_srgb(base)
	return color_to_rgb(ME.lerp(base_srgb, line_srgb, alpha_base_to_line))


def color_rotation(rgb: Annotated[float3, float3(1.0, 0.0, 0.0)], u_theta: Annotated[float, preview_alpha(0.2)]) -> float3:
	"""色相を回転

	Args:
		rgb: カラー
		u_theta: 回転角度 (0 ~ 1)
	Returns:
		カラー
	"""
	hsv = ME.rgb_to_hsv(rgb)
	return ME.hsv_to_rgb(float3((1.0 + hsv.x + u_theta) % 1.0, hsv.y, hsv.z))


def color_spectrum(intensity: Annotated[float, preview_distance()]) -> float3:
	"""強度を色に変換

	Args:
		intensity: 強度 (0 ~ 1)
	Returns:
		カラー
	"""
	return color_rotation(float3(1.0, 0.0, 0.0), intensity)
