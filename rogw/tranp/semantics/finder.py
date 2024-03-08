from rogw.tranp.compatible.python.types import Standards
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.module.types import LibraryPaths
from rogw.tranp.syntax.ast.dsn import DSN
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.errors import MustBeImplementedError, SymbolNotDefinedError
from rogw.tranp.semantics.reflection import IReflection, SymbolDB


class SymbolFinder:
	"""シンボル検索インターフェイス"""

	@injectable
	def __init__(self, library_paths: LibraryPaths) -> None:
		"""インスタンスを生成

		Args:
			library_paths (LibraryPaths): 標準ライブラリーパスリスト @inject
		"""
		self.__library_paths = [module_path.path for module_path in library_paths]

	def get_object(self, db: SymbolDB) -> IReflection:
		"""objectのシンボルを取得

		Args:
			db (SymbolDB): シンボルテーブル
		Returns:
			IReflection: シンボル
		Raises:
			MustBeImplementedError: objectが未実装
		Note:
			必ず存在すると言う前提。見つからない場合は実装ミス
		"""
		raw = self.__find_raw(db, self.__library_paths, object.__name__)
		if raw is not None:
			return raw

		raise MustBeImplementedError('"object" class is required.')

	def by(self, db: SymbolDB, fullyname: str) -> IReflection:
		"""完全参照名からシンボルを取得

		Args:
			db (SymbolDB): シンボルテーブル
			fullyname (str): 完全参照名
		Returns:
			IReflection: シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		if fullyname in db:
			return db[fullyname]

		raise SymbolNotDefinedError(f'fullyname: {fullyname}')

	def by_standard(self, db: SymbolDB, standard_type: type[Standards] | None) -> IReflection:
		"""標準クラスのシンボルを取得

		Args:
			db (SymbolDB): シンボルテーブル
			standard_type (type[Standards] | None): 標準クラス
		Returns:
			IReflection: シンボル
		Raises:
			MustBeImplementedError: 標準クラスが未実装
		"""
		domain_name = ''
		if standard_type is None:
			domain_name = 'None'
		else:
			domain_name = standard_type.__name__

		raw = self.__find_raw(db, self.__library_paths, domain_name)
		if raw is not None:
			return raw

		raise MustBeImplementedError(f'"{standard_type.__name__}" class is required.')

	def by_symbolic(self, db: SymbolDB, node: defs.Symbolic) -> IReflection:
		"""シンボル系ノードからシンボルを取得

		Args:
			db (SymbolDB): シンボルテーブル
			node: (Symbolic): シンボル系ノード
		Returns:
			IReflection: シンボル
		Raises:
			SymbolNotDefinedError: シンボルが見つからない
		"""
		raw = self.find_by_symbolic(db, node)
		if raw is not None:
			return raw

		raise SymbolNotDefinedError(f'fullyname: {node.fullyname}')

	def find_by_symbolic(self, db: SymbolDB, node: defs.Symbolic, prop_name: str = '') -> IReflection | None:
		"""シンボルを検索。未検出の場合はNoneを返却

		Args:
			db (SymbolDB): シンボルテーブル
			node (Symbolic): シンボル系ノード
			prop_name (str): プロパティー名(default = '')
		Returns:
			IReflection | None: シンボル
		"""
		def is_local_var_in_class_scope(scope: str) -> bool:
			# XXX ローカル変数の参照は、クラス直下のスコープを参照できない
			return node.is_a(defs.Var) and scope in db and db[scope].types.is_a(defs.Class)

		domain_name = DSN.join(node.domain_name, prop_name)
		# ドメイン名の要素数が1つの場合のみ標準ライブラリーへのフォールバックを許可する(プライマリー以外のモジュールへのフォールバックを抑制)
		allow_fallback_lib = DSN.elem_counts(domain_name) == 1
		scopes = [scope for scope in self.__make_scopes(node.scope, allow_fallback_lib) if not is_local_var_in_class_scope(scope)]
		return self.__find_raw(db, scopes, domain_name)

	def __find_raw(self, db: SymbolDB, scopes: list[str], domain_name: str) -> IReflection | None:
		"""スコープを辿り、指定のドメイン名を持つシンボルを検索。未検出の場合はNoneを返却

		Args:
			db (SymbolDB): シンボルテーブル
			scopes (list[str]): 探索スコープリスト
			domain_name (str): ドメイン名
		Returns:
			IReflection | None: シンボル
		"""
		candidates = [DSN.join(scope, domain_name) for scope in scopes]
		for candidate in candidates:
			if candidate in db:
				return db[candidate]

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
