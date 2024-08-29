from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.di import LazyDI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.loader import ModuleDependencyProvider
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entrypoints import EntrypointLoader
from rogw.tranp.syntax.ast.parser import SyntaxParser
from rogw.tranp.syntax.ast.query import Query
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


@injectable
def entrypoint_loader(locator: Locator, dependency_provider: ModuleDependencyProvider) -> EntrypointLoader:
	"""エントリーポイントローダーを生成

	Args:
		locator (Locator): ロケーター @inject
		dependency_provider (ModuleDependencyProvider): @inject
	Returns:
		EntrypointLoader: エントリーポイント
	"""
	def handler(module_path: ModulePath) -> defs.Entrypoint:
		shared_di = as_a(LazyDI, locator)
		# XXX 共有が必須のモジュールを事前に解決
		shared_di.resolve(SyntaxParser)
		shared_di.resolve(CacheProvider)
		dependency_di = LazyDI.instantiate(dependency_provider())
		new_di = shared_di.combine(dependency_di)
		new_di.rebind(Locator, lambda: new_di)
		new_di.rebind(Invoker, lambda: new_di.invoke)
		new_di.bind(ModulePath, lambda: module_path)
		return new_di.resolve(defs.Entrypoint)

	return handler


def entrypoint(query: Query[Node]) -> defs.Entrypoint:
	"""エントリーポイントを解決

	Args:
		query (Query[Node]): ノードクエリー
	Returns:
		Node: エントリーポイント
	"""
	return query.by('file_input').as_a(defs.Entrypoint)
