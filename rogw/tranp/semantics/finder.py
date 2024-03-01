from types import UnionType

from rogw.tranp.syntax.ast.dsn import DSN
from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.types import LibraryPaths
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.errors import MustBeImplementedError, SymbolNotDefinedError
from rogw.tranp.semantics.symbol import SymbolRaw, SymbolRaws


class SymbolFinder:
	"""シンボル検索インターフェイス"""

	@injectable
	def __init__(self, library_paths: LibraryPaths) -> None:
		"""インスタンスを生成

		Args:
			library_paths (LibraryPaths): 標準ライブラリーパスリスト @inject
		"""
		self.__library_paths = library_paths

	def get_object(self, raws: SymbolRaws) -> SymbolRaw:
		"""objectのシンボルを取得

		Args:
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaw: シンボル
		Raises:
			MustBeImplementedError: objectが未実装
		Note:
			必ず存在すると言う前提。見つからない場合は実装ミス
		"""
		raw = self.__find_raw(raws, self.__library_paths, object.__name__)
		if raw is not None:
			return raw

		raise MustBeImplementedError('"object" class is required.')

	def by(self, raws: SymbolRaws, fullyname: str) -> SymbolRaw:
		"""完全参照名からシンボルを取得

		Args:
			raws (SymbolRaws): シンボルテーブル
			fullyname (str): 完全参照名
		Returns:
			SymbolRaw: シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		if fullyname in raws:
			return raws[fullyname]

		raise SymbolNotDefinedError(f'fullyname: {fullyname}')

	def by_standard(self, raws: SymbolRaws, standard_type: type[Standards] | None) -> SymbolRaw:
		"""標準クラスのシンボルを取得

		Args:
			raws (SymbolRaws): シンボルテーブル
			standard_type (type[Standards] | None): 標準クラス
		Returns:
			SymbolRaw: シンボル
		Raises:
			MustBeImplementedError: 標準クラスが未実装
		"""
		domain_name = ''
		if standard_type is None:
			domain_name = 'None'
		elif standard_type is UnionType:
			domain_name = 'Union'
		else:
			domain_name = standard_type.__name__

		raw = self.__find_raw(raws, self.__library_paths, domain_name)
		if raw is not None:
			return raw

		raise MustBeImplementedError(f'"{standard_type.__name__}" class is required.')

	def by_symbolic(self, raws: SymbolRaws, node: defs.Symbolic) -> SymbolRaw:
		"""シンボル系ノードからシンボルを取得

		Args:
			raws (SymbolRaws): シンボルテーブル
			node: (Symbolic): シンボル系ノード
		Returns:
			SymbolRaw: シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		raw = self.find_by_symbolic(raws, node)
		if raw is not None:
			return raw

		raise SymbolNotDefinedError(f'fullyname: {node.fullyname}')

	def find_by_symbolic(self, raws: SymbolRaws, node: defs.Symbolic, prop_name: str = '') -> SymbolRaw | None:
		"""シンボルを検索。未検出の場合はNoneを返却

		Args:
			raws (SymbolRaws): シンボルテーブル
			node (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			SymbolRaw | None: シンボル
		"""
		def is_local_var_in_class_scope(scope: str) -> bool:
			# XXX ローカル変数の参照は、クラス直下のスコープを参照できない
			return node.is_a(defs.Var) and scope in raws and raws[scope].types.is_a(defs.Class)

		domain_name = DSN.join(node.domain_name, prop_name)
		# ドメイン名の要素数が1つの場合のみ標準ライブラリーへのフォールバックを許可する(プライマリー以外のモジュールへのフォールバックを抑制)
		allow_fallback_lib = DSN.elem_counts(domain_name) == 1
		scopes = [scope for scope in self.__make_scopes(node.scope, allow_fallback_lib) if not is_local_var_in_class_scope(scope)]
		return self.__find_raw(raws, scopes, domain_name)

	def __find_raw(self, raws: SymbolRaws, scopes: list[str], domain_name: str) -> SymbolRaw | None:
		"""スコープを辿り、指定のドメイン名を持つシンボルを検索。未検出の場合はNoneを返却

		Args:
			raws (SymbolRaws): シンボルテーブル
			scopes (list[str]): 探索スコープリスト
			domain_name (str): ドメイン名
		Returns:
			SymbolRaw | None: シンボル
		"""
		candidates = [DSN.join(scope, domain_name) for scope in scopes]
		for candidate in candidates:
			if candidate in raws:
				return raws[candidate]

		return None

	def __make_scopes(self, scope: str, allow_fallback_lib: bool = True) -> list[str]:
		"""スコープを元に探索スコープのリストを生成

		Args:
			scope (str): スコープ
			allow_fallback_lib (bool): True = 標準ライブラリーのパスを加える(default = True)
		Returns:
			list[str]: 探索スコープリスト
		"""
		scopes_of_node = [DSN.left(scope, DSN.elem_counts(scope) - i) for i in range(DSN.elem_counts(scope))]
		return [*scopes_of_node, *(self.__library_paths if allow_fallback_lib else [])]
