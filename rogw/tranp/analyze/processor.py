from typing import Callable, Protocol, TypeAlias

from rogw.tranp.analyze.symbol import SymbolRaws


# class Preprocessor(Protocol):
# 	"""プリプロセッサープロトコル"""
# 
# 	def __call__(self, *args: Any) -> SymbolRaws:
# 		"""シンボルテーブルを生成
# 
# 		Args:
# 			*args (Any): 位置引数
# 		Returns:
# 			SymbolRaws: シンボルテーブル
# 		Note:
# 			実行時にカリー化されるため、引数の最後に必ずSymbolRawsを定義する必要がある
# 		Example:
# 			```python
# 			class PreprocessorImpl:
# 				def __call__(self, inject_a: A, inject_b: B, raws: SymbolRaws) -> SymbolRaws:
# 					# some process
# 					...
# 			```
# 		"""
# 		...
# XXX 引数を可変にするとシグネチャーが一致しないと判断されるためTypeAliasで定義
Preprocessor: TypeAlias = Callable[..., SymbolRaws]


class Preprocessors(Protocol):
	"""プリプロセッサープロバイダープロトコル"""

	def __call__(self) -> list[Preprocessor]:
		"""プリプロセッサーリストを返却

		Returns:
			list[Preprocessor]: プリプロセッサーリスト
		"""
		raise NotImplementedError()
