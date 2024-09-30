import json
from typing import IO, NamedTuple

import rogw.tranp.compatible.libralies.classes as classes
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.io.cache import CacheProvider, Stored
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.trait import Traits
from rogw.tranp.module.modules import Module
from rogw.tranp.semantics.errors import SymbolNotDefinedError
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.processor import Preprocessor
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.reflection import Symbol
import rogw.tranp.syntax.node.definition as defs


class Expanded(NamedTuple):
	"""展開時のテンポラリーデータ

	Attributes:
		classes (dict[str, str]): クラス定義マップ
		decl_vars (dict[str, str]): 変数宣言マップ
		imports (dict[str, str]): インポートマップ
		import_paths (list[str]): インポートパスリスト
	"""

	classes: dict[str, str] = {}
	decl_vars: dict[str, str] = {}
	imports: dict[str, str] = {}
	import_paths: list[str] = []

	@classmethod
	@duck_typed(Stored)
	def load(cls, stream: IO) -> 'Expanded':
		""""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			Store: インスタンス
		"""
		values = json.load(stream)
		return Expanded(values[0], values[1], values[2], values[3])

	@duck_typed(Stored)
	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		stream.write(json.dumps(self, separators=(',', ':')).encode('utf-8'))


class ExpandModules:
	"""モジュール内のシンボルをシンボルテーブルに展開"""

	@injectable
	def __init__(self, finder: SymbolFinder, caches: CacheProvider, files: IFileLoader, traits: Traits[IReflection]) -> None:
		"""インスタンスを生成

		Args:
			finder (SymbolFinder): シンボル検索 @inject
			caches (CacheProvider): キャッシュプロバイダー @inject
			files (IFileLoader): ファイルローダー @inject
			traits (Traits[IReflection]): トレイトマネージャー @inject
		"""
		self.finder = finder
		self.caches = caches
		self.files = files
		self.traits = traits

	@duck_typed(Preprocessor)
	def __call__(self, module: Module, db: SymbolDB) -> bool:
		"""シンボルテーブルを編集

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		self.expanded_to_db(module, db, self.expand_module(module))
		return True

	def expanded_to_db(self, module: Module, db: SymbolDB, expanded: Expanded) -> None:
		"""展開データを基にシンボルテーブルを更新

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
			expanded (Expanded): 展開データ
		"""
		# クラス定義シンボルの展開
		for fullyname, full_path in expanded.classes.items():
			if fullyname not in db:
				types = module.entrypoint.whole_by(full_path).as_a(defs.ClassDef)
				db[fullyname] = Symbol.instantiate(self.traits, types).stack()

		# インポートシンボルの展開
		for fullyname, full_path in expanded.imports.items():
			if fullyname not in db:
				import_name = module.entrypoint.whole_by(full_path).as_a(defs.ImportAsName)
				import_node = import_name.declare.as_a(defs.Import)
				raw = db[ModuleDSN.full_joined(import_node.import_path.tokens, import_name.entity_symbol.tokens)]
				db[fullyname] = raw.stack(import_name)

		# 変数宣言シンボルの展開
		for fullyname, full_path in expanded.decl_vars.items():
			var = module.entrypoint.whole_by(full_path).one_of(*defs.DeclVarsTs)
			if var.symbol.fullyname not in db:
				raw = self.resolve_type_symbol(db, var)
				db[var.symbol.fullyname] = raw.declare(var)

	def expand_module(self, module: Module) -> Expanded:
		"""モジュールのシンボル・インポートパスを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		nodes = module.entrypoint.procedural()
		nodes.append(module.entrypoint)

		classes: dict[str, str] = {}
		decl_vars: dict[str, str] = {}
		imports: dict[str, str] = {}
		import_paths: list[str] = []
		for node in nodes:
			if isinstance(node, defs.ClassDef):
				classes[node.fullyname] = node.full_path

			if isinstance(node, defs.Entrypoint):
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Function):
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Enum):
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.vars}}
			elif isinstance(node, defs.Class):
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.class_vars}}
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.this_vars}}
			elif isinstance(node, defs.Generator):
				decl_vars = {**decl_vars, **{var.fullyname: var.full_path for var in node.decl_vars}}

			if isinstance(node, defs.Import):
				imports = {**imports, **{symbol.fullyname: symbol.full_path for symbol in node.symbols}}
				import_paths.append(node.import_path.tokens)

		return Expanded(classes, decl_vars, imports, import_paths)

	def resolve_type_symbol(self, db: SymbolDB, var: defs.DeclVars) -> IReflection:
		"""シンボルテーブルから変数の型のシンボルを解決

		Args:
			db (SymbolDB): シンボルテーブル
			var (DeclVars): 変数宣言ノード
		Returns:
			IReflection: シンボル
		Raises:
			SymbolNotDefinedError: シンボルの解決に失敗
		"""
		decl_type = self.fetch_decl_type(var)
		if decl_type is not None:
			symbol = self.finder.find_by_symbolic(db, decl_type)
			if symbol:
				return symbol

			fallback = self._fallback_type_symbol(db, decl_type)
			if fallback:
				return fallback

			raise SymbolNotDefinedError(f'fullyname: {var.fullyname}')
		else:
			return self.finder.by_standard(db, classes.Unknown)

	def fetch_decl_type(self, var: defs.DeclVars) -> defs.Type | defs.ClassDef | None:
		"""変数の型(タイプ/クラス定義ノード)を取得。型が不明な場合はNoneを返却

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			Type | ClassDef | None: タイプ/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(var.declare, defs.Parameter):
			if isinstance(var.declare.symbol, defs.DeclClassParam) and isinstance(var.declare.var_type, defs.Empty):
				return var.declare.symbol.class_types.as_a(defs.ClassDef)
			elif isinstance(var.declare.symbol, defs.DeclThisParam) and isinstance(var.declare.var_type, defs.Empty):
				return var.declare.symbol.class_types.as_a(defs.ClassDef)
			else:
				return var.declare.var_type.as_a(defs.Type)
		elif isinstance(var.declare, (defs.AnnoAssign, defs.Catch)):
			return var.declare.var_type
		elif isinstance(var.declare, (defs.MoveAssign, defs.For, defs.CompFor, defs.WithEntry)):
			# 型指定が無いため全てUnknown
			return None

		return None

	def _fallback_type_symbol(self, db: SymbolDB, decl_type: defs.Type | defs.ClassDef) -> IReflection | None:
		"""変数の型からシンボルを解決(フォールバック)

		Args:
			db (SymbolDB): シンボルテーブル
			decl_type (DeclVars): タイプ/クラス定義ノード
		Returns:
			IReflection | None: シンボル
		Note:
			### 解決対象
			* ParamSpecのargs/kwargs
		"""
		if not isinstance(decl_type, defs.RelayOfType):
			return None

		receiver_type = self.finder.by_symbolic(db, decl_type.receiver)
		if not isinstance(receiver_type.types, defs.TemplateClass):
			return None

		def_class = self.finder.by_symbolic(db, receiver_type.types.definition_type)
		return self.finder.find_by_symbolic(db, def_class.types, decl_type.prop.tokens)
