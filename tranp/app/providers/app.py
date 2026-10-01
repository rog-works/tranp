from tranp.app.app.env import DataEnvPath, SourceEnvPath
from tranp.app.file.loader import FileLoader, IFileLoader
from tranp.app.lang.annotation import injectable
from tranp.app.lang.di import DI, LazyDI, ModuleDefinitions
from tranp.app.lang.locator import Invoker, Locator


def di_container(definitions: ModuleDefinitions) -> DI:
	"""DIコンテナーを生成

	Args:
		definitions: モジュール定義
	Returns:
		DIコンテナー
	"""
	di = LazyDI.instantiate(definitions)
	di.bind(Locator, lambda: di)
	di.bind(Invoker, lambda: di.invoke)
	return di


@injectable
def data_loader(env_path: DataEnvPath) -> IFileLoader:
	"""ファイルローダー(データ用)を生成

	Args:
		env_path: 環境パスリスト @inject
	Returns:
		ファイルローダー
	"""
	return FileLoader(env_path.paths)


@injectable
def source_loader(env_path: SourceEnvPath) -> IFileLoader:
	"""ファイルローダー(ソースコード用)を生成

	Args:
		env_path: 環境パスリスト @inject
	Returns:
		ファイルローダー
	"""
	return FileLoader(env_path.paths)
