from colorsys import hsv_to_rgb, rgb_to_hsv
from typing import TypeVar

from numpy import atan2 as np_atan2
from numpy import cos as np_cos
from numpy import dot as np_dot
from numpy import floor as np_floor
from numpy import pi as np_pi
from numpy import power as np_power
from numpy import random as np_random
from numpy import sin as np_sin
from numpy import tan as np_tan

from example.material.me_types import SamplerTypes, float2, float3, float4, texture
from tranp.app.lang.annotation import deprecated

T_Value = TypeVar('T_Value', float, float2, float3, float4)
T_Vector = TypeVar('T_Vector', float2, float3, float4)


class ME:
	"""マテリアル関数式"""

	# region 定数

	@classmethod
	def pi(cls) -> float:
		"""Returns: PI"""
		return float(np_pi)

	# endregion
	# region 公開パラメーター

	@classmethod
	def ex_bool(cls, value: bool, desc: str) -> bool:
		"""公開パラメーター(bool)を作成

		Args:
			value: 初期値
			desc: コメント
		Returns:
			真偽値
		"""
		return value

	@classmethod
	def ex_float(cls, value: float, desc: str, minimum: float, maximum: float) -> float:
		"""公開パラメーター(float)を作成

		Args:
			value: 初期値
			desc: コメント
			minimum: 下限値
			maximum: 上限値
		Returns:
			値
		"""
		return value

	@classmethod
	def ex_float3(cls, x: float, y: float, z: float, desc: str) -> float3:
		"""公開パラメーター(float3)を作成

		Args:
			x: X座標
			y: Y座標
			z: Z座標
			desc: コメント
		Returns:
			ベクトル(3次元)
		Note:
			```
			XXX 定義上の型はfloat4だが、実態としてはfloat3として扱われている模様
			XXX aを使えないケースが多々あるため、予めfloat3として扱う
			```
		"""
		return float3(x, y, z)

	@classmethod
	def ex_texture(cls, src: str, desc: str, sampler: str = SamplerTypes.Color.value) -> texture:
		"""公開パラメーター(texture)を作成

		Args:
			src: テクスチャーソースパス
			desc: コメント
			sampler: テクスチャーサンプル種別 (default = 'Color')
		Returns:
			テクスチャー
		"""
		return texture(src)

	# endregion
	# region 算術演算

	@classmethod
	def abs(cls, value: T_Value) -> T_Value:
		"""絶対値を返す

		Args:
			value: 値
		Returns:
			絶対値
		"""
		if isinstance(value, float2):
			return float2(abs(value.x), abs(value.y))
		elif isinstance(value, float3):
			return float3(abs(value.x), abs(value.y), abs(value.z))
		elif isinstance(value, float4):
			return float4(abs(value.x), abs(value.y), abs(value.z), abs(value.w))
		else:
			return abs(value)

	@classmethod
	def power(cls, value: T_Value, exponent: float) -> T_Value:
		"""べき乗

		Args:
			value: 値
			exponent: 指数
		Returns:
			べき乗した値
		"""
		if isinstance(value, float2):
			return float2(np_power(value.x, exponent), np_power(value.y, exponent))
		elif isinstance(value, float3):
			return float3(np_power(value.x, exponent), np_power(value.y, exponent), np_power(value.z, exponent))
		elif isinstance(value, float4):
			return float4(np_power(value.x, exponent), np_power(value.y, exponent), np_power(value.z, exponent), np_power(value.w, exponent))
		else:
			return float(np_power(value, exponent))

	@classmethod
	def sign(cls, value: float) -> float:
		"""符号を返す

		Args:
			value: 値
		Returns:
			1 or 0 or -1
		Note:
			XXX proxy_signは単一の型しか受け取れないためfloatのみとする
		"""
		return 1.0 if value > 0 else (-1.0 if value < 0 else 0.0)

	# endregion
	# region 乱数

	@classmethod
	def rand_fast(cls, vector: float2, seed: float) -> float:
		"""ベクトルを基に乱数を生成。0 ~ 1の範囲は同じ乱数値になる

		Args:
			vector: ベクトル
			seed: シード値
		Returns:
			乱数
		"""
		v = cls.abs(vector)
		# XXX 通常被らない程度の範囲でシード値を生成
		seeds = [str(int(v.x)), str(int(v.y)), str(int(seed))]
		join_seed = ''.join([f'{"000"[:-len(s)]}{s}' for s in seeds])
		np_random.seed(int(f'1{join_seed}'))
		return float(np_random.rand())

	# endregion
	# region クランプ

	@classmethod
	def clamp(cls, value: T_Value, minimum: float, maximum: float) -> T_Value:
		"""値を範囲内でクランプ

		Args:
			value: 値
			minimum: 下限値
			maximum: 上限値
		Returns:
			float or ベクトル
		Note:
			min/maxを初期値で利用する場合はsaturateを使用することを推奨
		"""
		if isinstance(value, float2):
			return float2(cls.clamp(value.x, minimum, maximum), cls.clamp(value.y, minimum, maximum))
		elif isinstance(value, float3):
			return float3(cls.clamp(value.x, minimum, maximum), cls.clamp(value.y, minimum, maximum), cls.clamp(value.z, minimum, maximum))
		elif isinstance(value, float4):
			return float4(cls.clamp(value.x, minimum, maximum), cls.clamp(value.y, minimum, maximum), cls.clamp(value.z, minimum, maximum), cls.clamp(value.w, minimum, maximum))
		else:
			return min(maximum, max(minimum, value))

	@classmethod
	def floor(cls, value: T_Value) -> T_Value:
		"""少数を切り捨て、より小さい整数にする

		Args:
			value: 値
		Returns:
			整数部
		"""
		if isinstance(value, float2):
			return float2(float(np_floor(value.x)), float(np_floor(value.y)))
		elif isinstance(value, float3):
			return float3(float(np_floor(value.x)), float(np_floor(value.y)), float(np_floor(value.z)))
		elif isinstance(value, float4):
			return float4(float(np_floor(value.x)), float(np_floor(value.y)), float(np_floor(value.z)), float(np_floor(value.w)))
		else:
			return float(np_floor(value))

	@classmethod
	def max(cls, a: T_Value, b: float) -> T_Value:
		"""大きい方の値を返す

		Args:
			a: 値
			b: 値
		Returns:
			大きい方の値
		"""
		if isinstance(a, float2):
			return float2(max(a.x, b), max(a.y, b))
		elif isinstance(a, float3):
			return float3(max(a.x, b), max(a.y, b), max(a.z, b))
		elif isinstance(a, float4):
			return float4(max(a.x, b), max(a.y, b), max(a.z, b), max(a.w, b))
		else:
			return max(a, b)

	@classmethod
	def min(cls, a: T_Value, b: float) -> T_Value:
		"""小さい方の値を返す

		Args:
			a: 値
			b: 値
		Returns:
			小さい方の値
		"""
		if isinstance(a, float2):
			return float2(min(a.x, b), min(a.y, b))
		elif isinstance(a, float3):
			return float3(min(a.x, b), min(a.y, b), min(a.z, b))
		elif isinstance(a, float4):
			return float4(min(a.x, b), min(a.y, b), min(a.z, b), min(a.w, b))
		else:
			return min(a, b)

	@classmethod
	def saturate(cls, value: T_Value) -> T_Value:
		"""値を0 ~ 1の範囲でクランプ

		Args:
			value: 値
		Returns:
			float or ベクトル
		Note:
			clamp(x, 0, 1)と数学的には等価。HLSL的に高速
		"""
		return cls.clamp(value, 0.0, 1.0)

	@classmethod
	@deprecated
	def trunc(cls, value: float) -> float:
		"""少数を切り捨て

		Args:
			value: 値
		Returns:
			整数部
		Note:
			@deprecated APIが非公開であり、移植性が低いため使用禁止とする
		"""
		raise ValueError

	# endregion
	# region 線形補完・ステップ関数

	@classmethod
	def lerp(cls, a: T_Value, b: T_Value, alpha: float) -> T_Value:
		"""AからBに向かって線形補完した値を返す

		Args:
			a: 始点
			b: 終点
			alpha: α値
		Returns:
			float or ベクトル
		"""
		b_alpha = cls.saturate(alpha)
		a_alpha = 1.0 - b_alpha
		return (a * a_alpha) + (b * b_alpha)

	@classmethod
	def smoothstep(cls, minimum: float, maximum: float, value: float) -> float:
		"""閾値以内を0 ~ 1まで緩やかに補完, 下限値未満は0を返す

		Args:
			minimum: 下限値
			maximum: 上限値
			value: 値
		Returns:
			0 ~ 1
		Note:
			Cosの半周(0 ~ 180度)を上下反転した波形とほぼ同等
		"""
		size = maximum - minimum
		diff = value - minimum
		c = cls.cos(cls.saturate(diff / size), 2.0)
		return 1.0 - (c * 0.5 + 0.5)

	@classmethod
	def step(cls, value: float, threshold: float) -> float:
		"""閾値以内は1, それ以外は0を返す

		Args:
			value: 値
			threshold: 閾値
		Returns:
			0 or 1
		"""
		return 1.0 if value <= threshold else 0.0

	# endregion
	# region 三角関数

	@classmethod
	def atan2_fast(cls, y: float, x: float) -> float:
		"""Arctangent2Fast。XY座標を基に弧度(ラジアン)を算出

		Args:
			y: Y座標
			x: X座標
		Returns:
			弧度(ラジアン)
		Note:
			```
			* fastの精度誤差は0.001 ~ 0.005rad程度であり、殆ど無視出来るレベル
			* 出力値は-PI ~ 0 ~ PI
			```
		"""
		return float(np_atan2(y, x))

	@classmethod
	def dot(cls, a: float, b: float) -> float:
		"""内積

		Args:
			a: 値
			b: 値
		Returns:
			内積
		"""
		return float(np_dot(a, b))

	@classmethod
	def cos(cls, ratio: float, period: float = 1.0) -> float:
		"""Cosine。0=1.0, 0.5=0.0, 1=1.0

		Args:
			ratio: 1周の割合
			period: 1周の単位 (default = 1.0)
		Returns:
			0 ~ 1
		Note:
			一般的なcosとは違い、半周(PI)ではなく1周(PI * 2)を基数とする点に注意
		Examples:
			```python
			ME.cos(degree / 360.0)
			ME.cos(radian / (ME.pi() * 2.0))
			# 上記と等価
			ME.cos(degree, 360.0)
			ME.cos(radian, ME.pi() * 2.0)
			```
		"""
		radian = float(np_pi * 2.0 * (ratio / period))
		return float(np_cos(radian))

	@classmethod
	def sin(cls, ratio: float, period: float = 1.0) -> float:
		"""Sine。0=0.0, 0.5=1.0, 1=0.0

		Args:
			ratio: 1周の割合
			period: 1周の単位 (default = 1.0)
		Returns:
			0 ~ 1
		Note:
			@see cos#Note
		"""
		radian = float(np_pi * 2.0 * (ratio / period))
		return float(np_sin(radian))

	@classmethod
	def tan(cls, ratio: float, period: float = 1.0) -> float:
		"""Tangent

		Args:
			ratio: 1周の割合
			period: 1周の単位 (default = 1.0)
		Returns:
			0 ~ 1
		Note:
			@see cos#Note
		"""
		radian = float(np_pi * 2.0 * (ratio / period))
		return float(np_tan(radian))

	# endregion
	# region カラーコード変換

	@classmethod
	def rgb_to_hsv(cls, rgb: float3) -> float3:
		"""RGBをHSVに変換

		Args:
			rgb: RGB
		Returns:
			HSV
		"""
		return float3(*rgb_to_hsv(rgb.x, rgb.y, rgb.z))

	@classmethod
	def hsv_to_rgb(cls, hsv: float3) -> float3:
		"""HSVをRGBに変換

		Args:
			hsv: HSV
		Returns:
			RGB
		"""
		return float3(*hsv_to_rgb(hsv.x, hsv.y, hsv.z))

	@classmethod
	def rgb_to_srgb(cls, rgb: float) -> float:
		"""RGBをsRGBに変換

		Args:
			rgb: 値 ※シェーダーの仕様でfloatのみ対応
		Returns:
			sRGB
		"""
		return cls.power(rgb, 1.0 / 2.2)

	@classmethod
	def srgb_to_rgb(cls, srgb: float) -> float:
		"""sRGBをRGBに変換

		Args:
			srgb: 値 ※シェーダーの仕様でfloatのみ対応
		Returns:
			RGB
		"""
		return cls.power(srgb, 2.2)

	# endregion
	# region テクスチャー操作

	@classmethod
	def panner(cls, uv: float2, speed: float2) -> float2:
		"""UV座標スクロール

		Args:
			uv: UV座標
			speed: 速度倍率
		Returns:
			UV座標
		Note:
			XXX Python上は入力したUV座標をそのまま返す
		"""
		return uv

	@classmethod
	def tex_coord(cls, index: int) -> float2:
		"""UV座標を生成

		Args:
			index: UVインデックス
		Returns:
			UV座標
		"""
		return float2()

	@classmethod
	def sample(cls, texture: texture, uv: float2, sampler: str = SamplerTypes.Color.value) -> float4:
		"""テクスチャーサンプリングを生成

		Args:
			texture: テクスチャー
			uv: UV座標
			sampler: テクスチャーサンプル種別 (default = 'Color')
		Returns:
			RGBA
		Note:
			XXX samplerはテクスチャーオブジェクトのsamplerと一致させる必要がある点に注意
		"""
		return float4()

	# endregion
	# region ピクセルシェーダー

	@classmethod
	def ddx(cls, value: T_Value) -> T_Value:
		"""指定の値と隣接ピクセルとの勾配を取得(X方向)

		Args:
			value: 値 (float|float2)
		Returns:
			勾配
		Note:
			XXX 再現出来ないため適当な値を返す
		"""
		if isinstance(value, float):
			return 1.0
		elif isinstance(value, float2):
			return float2(1.0, 1.0)
		else:
			raise ValueError(value)

	@classmethod
	def ddy(cls, value: T_Value) -> T_Value:
		"""指定の値と隣接ピクセルとの勾配を取得(Y方向)

		Args:
			value: 値 (float|float2)
		Returns:
			勾配
		"""
		return cls.ddx(value)

	# endregion
	# region パラメーターコレクション

	@classmethod
	def const_by(cls, name: str) -> float:
		"""パラメーターコレクションから定数を取得(float)

		Args:
			name: パラメーター名
		Returns:
			値
		"""
		to_values = {'dpi_scale': 0.666}
		return to_values[name]

	# endregion
	# region 時間

	@classmethod
	def time(cls) -> float:
		"""経過時間を取得

		Returns:
			経過時間
		Note:
			XXX Python上は1.0を固定で返す
		"""
		return 1.0

	# endregion
