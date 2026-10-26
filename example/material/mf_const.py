from enum import Enum


class MFImages(Enum):
	"""マテリアル関数用画像

	Attributes:
		Noise: T_Noise
		NoiseLinear: T_Noise (LinearColor版)
		Easings: イージングカーブ
	"""
	Noise = 'T_Noise01'
	NoiseLinear = 'T_Noise01_Linear'
	Easings = 'easings'
