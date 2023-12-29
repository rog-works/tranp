from typing import Callable

from py2cpp.app.config import default_definitions
from py2cpp.app.provider import di_container
from py2cpp.app.types import ModuleDefinitions
from py2cpp.lang.locator import T_Inst


class App:
	"""アプリケーションランナー"""

	def __init__(self, definitions: ModuleDefinitions) -> None:
		"""インスタンスを生成

		Args:
			definitions (ModuleDefinitions): モジュール定義
		"""
		self.__di = di_container({**default_definitions(), **definitions})

	def run(self, task: Callable[..., T_Inst]) -> T_Inst:
		"""アプリケーションを実行

		Args:
			task (Callable[..., T_Inst]): タスクランナー
		Returns:
			T_Inst: 実行結果
		"""
		return self.__di.invoke(task)

	def resolve(self, symbol: type[T_Inst]) -> T_Inst:
		"""シンボルからインスタンスを解決

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
		Raises:
			ValueError: 未登録のシンボルを指定
		Note:
			XXX 出来れば消したい
		"""
		return self.__di.resolve(symbol)
