from py2cpp.analize.symbol import Expanded, SymbolRaw, SymbolRaws
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Module, Modules
import py2cpp.node.definition as defs


class Initializer:
	"""モジュールからシンボルテーブルの生成
	
	Note:
		プリプロセッサーの最初に実行することが前提
	"""

	@injectable
	def __call__(self, modules: Modules, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		main = modules.main

		# メインモジュールを展開
		expends: dict[Module, Expanded] = {}
		expends[main] = self.__expand_module(main)

		# インポートモジュールを全て展開
		import_index = 0
		import_modules_from_main = [modules.load(node.import_path.tokens) for node in expends[main].import_nodes]
		import_modules: dict[str, Module] = {**{module.path: module for module in modules.libralies}, **{module.path: module for module in import_modules_from_main}}
		while import_index < len(import_modules):
			import_module = list(import_modules.values())[import_index]
			expanded = self.__expand_module(import_module)
			import_modules_from_depended = [modules.load(node.import_path.tokens) for node in expanded.import_nodes]
			import_modules = {**import_modules, **{module.path: module for module in import_modules_from_depended}}
			expends[import_module] = expanded
			import_index += 1

		all_modules = {**import_modules, main.path: main}
		for expand_module in all_modules.values():
			expand_target = expends[expand_module]

			# 標準ライブラリを展開
			if expand_module not in modules.libralies:
				for core_module in modules.libralies:
					# 第1層で宣言されているシンボルに限定
					entrypoint = core_module.entrypoint.as_a(defs.Entrypoint)
					primary_symbol_names = [node.symbol.tokens for node in entrypoint.statements if isinstance(node, defs.DeclAll)]
					expanded = expends[core_module]
					filtered_db = {raw.path_to(expand_module): raw.to(expand_module) for raw in expanded.raws.values() if raw.symbol.tokens in primary_symbol_names}
					expand_target.raws = {**filtered_db, **expand_target.raws}

			# インポートモジュールを展開
			# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
			# XXX また、ステートメントのスコープも合わせて考慮
			for import_node in expand_target.import_nodes:
				# import句で明示されたシンボルに限定
				imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
				import_module = modules.load(import_node.import_path.tokens)
				expanded = expends[import_module]
				filtered_db = {raw.path_to(expand_module): raw.to(expand_module) for raw in expanded.raws.values() if raw.symbol.tokens in imported_symbol_names}
				expand_target.raws = {**filtered_db, **expand_target.raws}

			# 展開対象モジュールの変数シンボルを展開
			for var in expand_target.decl_vars:
				expand_target.raws[var.symbol.fullyname] = self.__resolve_var_type(var, expand_target.raws).varnize(var)

		# シンボルテーブルを統合
		new_raws = {**raws}
		for expanded in expends.values():
			new_raws = {**expanded.raws, **new_raws}

		return new_raws

	def __expand_module(self, module: Module) -> Expanded:
		"""モジュールの全シンボルを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		raws: dict[str, SymbolRaw] = {}
		decl_vars: list[defs.DeclVars] = []
		import_nodes: list[defs.Import] = []
		entrypoint = module.entrypoint.as_a(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.ClassDef):
				raws[node.fullyname] = SymbolRaw(node.fullyname, node.fullyname, module, node.symbol, node, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if isinstance(node, defs.Function):
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.class_vars)
				decl_vars.extend(node.this_vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		# XXX calculatedに含まれないためエントリーポイントは個別に処理
		decl_vars = [*entrypoint.decl_vars, *decl_vars]

		return Expanded(raws, decl_vars, import_nodes)

	def __resolve_var_type(self, var: defs.DeclVars, raws: SymbolRaws) -> SymbolRaw:
		"""シンボルテーブルから変数の型を解決

		Args:
			var (DeclVars): 変数宣言ノード
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaw: シンボルデータ
		"""
		domain_type = self.__fetch_domain_type(var)
		if domain_type is not None:
			scopes = [DSN.left(domain_type.scope, DSN.elem_counts(domain_type.scope) - i) for i in range(DSN.elem_counts(domain_type.scope))]
			candidates = [DSN.join(scope, domain_type.domain_name) for scope in scopes]
		else:
			# 型が不明な変数はUnknownにフォールバック
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			candidates = [DSN.join(var.module_path, 'Unknown')]

		for candidate in candidates:
			if candidate in raws:
				return raws[candidate]

		raise LogicError(f'Unresolve var type. var: {var}, domain: {domain_type.fullyname if domain_type is not None else "Unknown"}, candidates: {candidates}')

	def __fetch_domain_type(self, var: defs.DeclVars) -> defs.Type | defs.ClassDef | None:
		"""変数の型のドメインを取得。型が不明な場合はNoneを返却

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			Type | ClassDef | None: 型/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(var, (defs.AnnoAssign, defs.Catch)):
			return var.var_type
		elif isinstance(var, defs.Parameter):
			if isinstance(var.symbol, defs.DeclClassParam):
				return var.symbol.class_types.as_a(defs.ClassDef)
			elif isinstance(var.symbol, defs.DeclThisParam):
				return var.symbol.class_types.as_a(defs.ClassDef)
			else:
				return var.var_type.as_a(defs.Type)
		elif isinstance(var, (defs.MoveAssign, defs.For)):
			# 型指定が無いため全てUnknown
			return None

		return None
