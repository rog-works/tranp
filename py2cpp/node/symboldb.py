from typing import NamedTuple, TypeAlias

from py2cpp.ast.path import EntryPath
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class SymbolRow(NamedTuple):
	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Symbol
	types: defs.Types


SymbolDB: TypeAlias = dict[str, SymbolRow]
DeclVar: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign


class SymbolDBFactory:
	@classmethod
	def create(cls, modules: Modules) -> SymbolDB:
		main = modules.main
		db, decl_vars, import_nodes = cls.__pluck_main(main)

		# インポートモジュールの追加
		# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
		# XXX また、ステートメントのスコープも合わせて考慮
		for import_node in import_nodes:
			module = modules.load(import_node.module_path.tokens)
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# import句で明示したシンボルに限定
			imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.tokens in imported_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

		# 標準ライブラリの追加
		for module in modules.core_libralies:
			imported_db = cls.__pluck_imported(main, module)
			expanded_db = {
				row.org_path: SymbolRow(row.org_path, row.org_path, row.module, row.symbol, row.types)
				for _, row in imported_db.items()
			}
			# 第1層で宣言されているTypesに限定
			primary_symbol_names = [
				node.symbol.tokens
				for node in module.entrypoint(defs.Entrypoint).statements
				if isinstance(node, defs.Types)
			]
			filtered_db = {
				path: row
				for path, row in imported_db.items()
				if row.symbol.tokens in primary_symbol_names
			}
			db = {**expanded_db, **filtered_db, **db}

			# XXX インポートモジュール側にも展開
			for import_node in import_nodes:
				filtered_db = {
					path.replace(row.module.path, import_node.module.path): row
					for path, row in imported_db.items()
					if row.symbol.tokens in primary_symbol_names
				}
				db = {**filtered_db, **db}

		for var in decl_vars:
			# Thisは登録から除外
			if var.symbol.is_a(defs.This):
				pass
			# ThisVarはクラス直下に配置
			if var.symbol.is_a(defs.ThisVar):
				path = EntryPath.join(var.namespace, EntryPath(var.symbol.tokens).last()[0])
				ref_path = EntryPath.join(var.module.path, cls.__resolve_type_name(var))
				db[path.origin] = db[ref_path.origin]
			# それ以外はスコープ配下に配置
			else:
				scope = var.scope if type(var) is not defs.Parameter else var.parent.as_a(defs.Function).block.scope
				path = EntryPath.join(scope, var.symbol.tokens)
				db[path.origin] = cls.__resolve_symbol(var, db)

		# 基底クラスのシンボルを派生クラスに展開
		for row in list(db.values()):
			if not row.types.is_a(defs.Class):
				continue

			if row.module != main:
				continue

			sub_class = row.types.as_a(defs.Class)
			db = {**db, **cls.__expand_parent_symbols(main, sub_class, db)}

		return db

	@classmethod
	def __expand_parent_symbols(cls, expand_module: Module, sub_class: defs.Class, db: SymbolDB) -> SymbolDB:
		in_db: SymbolDB = {}
		for parent in sub_class.parents:
			path = EntryPath.join(expand_module.path, parent.tokens)
			parent_class = db[path.origin].types.as_a(defs.Class)
			for var in parent_class.vars:
				org_path = EntryPath.join(var.namespace, EntryPath(var.symbol.tokens).last()[0])
				path = EntryPath.join(sub_class.block.namespace, org_path.relativefy(var.namespace).origin)
				in_db[path.origin] = db[org_path.origin]

			in_db = {**cls.__expand_parent_symbols(expand_module, parent_class, db), **in_db}

		return in_db

	@classmethod
	def __pluck_main(cls, module: Module) -> tuple[SymbolDB, list[DeclVar], list[defs.Import]]:
		db: SymbolDB = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		for node in module.entrypoint(defs.Entrypoint).calculated():
			if isinstance(node, defs.Types):
				path = EntryPath.join(node.scope, node.symbol.tokens)
				db[path.origin] = SymbolRow(path.origin, path.origin, node.module, node.symbol, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Entrypoint:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Function:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Constructor:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		return db, decl_vars, import_nodes

	@classmethod
	def __pluck_imported(cls, expand_module: Module, imported: Module) -> SymbolDB:
		db: SymbolDB = {}
		for node in imported.entrypoint(defs.Entrypoint).calculated():
			# FIXME 一旦Typesに限定
			if isinstance(node, defs.Types):
				org_path = EntryPath.join(node.scope, node.symbol.tokens)
				path = EntryPath.join(expand_module.path, org_path.relativefy(node.module.path).origin)
				db[path.origin] = SymbolRow(path.origin, org_path.origin, expand_module, node.symbol, node)

		return db

	@classmethod
	def __resolve_symbol(cls, var: DeclVar, db: SymbolDB) -> SymbolRow:
		type_name = cls.__resolve_type_name(var)
		candidates = [
			EntryPath.join(var.scope, type_name),
			EntryPath.join(var.module.path, type_name),
		]
		for candidate in candidates:
			if candidate.origin in db:
				return db[candidate.origin]

		raise LogicError(f'Unresolve var type symbol. symbol: {var.symbol.tokens}')

	@classmethod
	def __resolve_type_name(cls, var: DeclVar) -> str:
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.var_type.is_a(defs.Symbol):
				return var.var_type.tokens
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol.tokens

		# XXX Unknownの名前は重要なので定数化などの方法で明示
		return 'Unknown'
