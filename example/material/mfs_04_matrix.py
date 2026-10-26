from typing import Annotated

from example.material.me import ME
from example.material.me_types import float2, float3
from example.material.mfs_00_preview import preview_vector


def matrix_rotation2d(vector: Annotated[float2, preview_vector()], u_theta: Annotated[float, 0.0]) -> float2:
	"""ベクトルを回転

	Args:
		vector: ベクトル
		u_theta: 回転角度 (0 ~ 1)
	Returns:
		ベクトル
	"""
	xv = vector * ME.cos(u_theta)
	yv = vector * ME.sin(u_theta)
	return float2(xv.x - yv.y, yv.x + xv.y)


def matrix_rotation_around_axis(vector: Annotated[float3, float3(1.0, 0.0, 0.0)], axis: Annotated[float3, float3(0.0, 1.0, 0.0)], u_theta: Annotated[float, 0.0]) -> float3:
	"""ベクトルを軸周りに回転

	Args:
		vector: ベクトル
		axis: 回転軸
		u_theta: 回転角度 (0 ~ 1)
	Returns:
		ベクトル
	"""
	c = ME.cos(u_theta)
	s = ME.sin(u_theta)

	a2 = axis * axis
	a3 = axis * float3(axis.y, axis.z, axis.x)
	a4 = axis * s

	ic = 1.0 - c

	xv = float3(ic * a2.x +    c, ic * a3.x + a4.z, ic * a3.z - a4.y) * vector.x
	yv = float3(ic * a3.x - a4.z, ic * a2.y +    c, ic * a3.y + a4.x) * vector.y
	zv = float3(ic * a3.z + a4.y, ic * a3.y - a4.x, ic * a2.z +    c) * vector.z
	return xv + yv + zv
