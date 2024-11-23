from rogw.tranp.app.env import DataEnvPath, SourceEnvPath
from rogw.tranp.app.loader import FileLoader
from rogw.tranp.file.loader import IFileLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.di import DI, LazyDI, ModuleDefinitions
from rogw.tranp.lang.locator import Invoker, Locator


def di_container(definitions: ModuleDefinitions) -> DI:
	"""DIコンテナーを生成

	Args:
		definitions (ModuleDefinitions): モジュール定義
	Returns:
		DI: DIコンテナー
	"""
	di = LazyDI.instantiate(definitions)
	di.bind(Locator, lambda: di)
	di.bind(Invoker, lambda: di.invoke)
	return di


def data_env_path() -> DataEnvPath:
	"""環境パス(データ用)を生成

	Returns:
		DataEnvPath: 環境パス(データ用)
	"""
	return DataEnvPath.instantiate()


def source_env_path() -> SourceEnvPath:
	"""環境パス(ソースコード用)を生成

	Returns:
		SourceEnvPath: 環境パス(ソースコード用)
	"""
	return SourceEnvPath.instantiate([])


@injectable
def data_loader(env_paths: DataEnvPath) -> IFileLoader:
	"""ファイルローダー(データ用)を生成

	Args:
		env_paths (DataEnvPath): 環境パスリスト @inject
	Returns:
		IFileLoader: ファイルローダー
	"""
	return FileLoader(env_paths)


@injectable
def source_loader(env_paths: SourceEnvPath) -> IFileLoader:
	"""ファイルローダー(ソースコード用)を生成

	Args:
		env_paths (SourceEnvPath): 環境パスリスト @inject
	Returns:
		IFileLoader: ファイルローダー
	"""
	return FileLoader(env_paths)
