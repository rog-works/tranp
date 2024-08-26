from typing import cast

from rogw.tranp.data.meta.types import ModuleMeta, ModuleMetaFactory
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.di import LazyDI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleDependencyProvider, ModuleLoader
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.syntax.ast.parser import SyntaxParser


def module_path_dummy() -> ModulePath:
	"""ダミーのモジュールパスを生成

	Returns:
		ModulePath: モジュールパス
	Note:
		モジュール経由で読み込みが不要な一部のテストでのみ利用
	"""
	return ModulePath('__main__', language='py')


def library_paths() -> ModulePaths:
	"""標準ライブラリーモジュールのパスリストを生成

	Returns:
		ModulePaths: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('rogw.tranp.compatible.libralies.classes', language='py')])


def module_paths() -> ModulePaths:
	"""処理対象モジュールのパスリストを生成

	Returns:
		ModulePath: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('example.example', language='py')])


@injectable
def module_loader(locator: Locator, dependency_provider: ModuleDependencyProvider, db: SymbolDB, preprocessors: Preprocessors) -> ModuleLoader:
	"""モジュールローダーを生成

	Args:
		locator (Locator): ロケーター @inject
		dependency_provider (ModuleDependencyProvider): @inject
		db (SymbolDB): シンボルテーブル @inject
		preprocessors (Preprocessors): プリプロセッサープロバイダー @inject
	Returns:
		ModuleLoader: モジュールローダー
	"""
	def preprocess(module: Module) -> Module:
		procs = preprocessors()
		for proc in procs:
			proc(module, db)

		return module

	def handler(module_path: ModulePath) -> Module:
		shared_di = cast(LazyDI, locator)
		# XXX 共有が必須のモジュールを事前に解決
		shared_di.resolve(SyntaxParser)
		shared_di.resolve(CacheProvider)
		dependency_di = LazyDI.instantiate(dependency_provider())
		new_di = shared_di.combine(dependency_di)
		new_di.rebind(Locator, lambda: new_di)
		new_di.rebind(Invoker, lambda: new_di.invoke)
		new_di.bind(ModulePath, lambda: module_path)
		return new_di.invoke(preprocess)

	return handler


@injectable
def module_meta_factory(module_paths: ModulePaths, loader: IFileLoader) -> ModuleMetaFactory:
	"""モジュールメタファクトリーを生成

	Args:
		module_paths (ModulePaths): モジュールパスリスト
		loader (IFileLoader): ファイルローダー
	Returns:
		ModuleMetaFactory: モジュールメタファクトリー
	"""
	def handler(module_path: str) -> ModuleMeta:
		index = [module_path.path for module_path in module_paths].index(module_path)
		target_module_path = module_paths[index]
		filepath = module_path_to_filepath(target_module_path.path, f'.{target_module_path.language}')
		return {'hash': loader.hash(filepath), 'path': module_path}

	return handler
