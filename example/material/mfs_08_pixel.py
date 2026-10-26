from typing import Annotated

from example.material.me import ME
from example.material.mfs_00_preview import preview_distance


def pixel_antialias(intensity: Annotated[float, preview_distance()]) -> float:
	"""強度からα値を算出

	Args:
		intensity: 強度 (0 ~ 1)
	Returns:
		α値
	Note:
		```
		### 利用条件
		* 強度はUV座標を基に算出
		* 周辺ピクセルとの強度の勾配は関数的な連続性が必要
		### 非利用条件
		* UV座標を基にしていても、画像の様な非連続的な強度に対しては効果が無い
		### DDX/DDYの必要性
		* 強度が関数的なら定数で割った方が効率が良く結果もほぼ等しい様に思えるが、結果は伴わない
		* 定数: 解像度によって強度の勾配が変化してしまう上、そもそも勾配を考慮できないため、極端な勾配になると中間値が無くなりアンチエイリアスが利かない
		* DDX/DDY: 解像度が変化したり、極端な勾配であってもある程度均一な結果になる
		```
	"""
	dx = ME.abs(ME.ddx(intensity))
	dy = ME.abs(ME.ddy(intensity))
	# 下限値: 0除算の対処
	# 上限値: 数値に必然性はなく、0.5 ~ 1.0程度が適量。大きいほどアンチエイリアスが利く半面、極端に小さい・細い図形が潰れる。DPIスケールと相関性がある？
	width = ME.clamp(dx + dy, 0.001, 0.7)
	return ME.saturate((1.0 - intensity) / width)
