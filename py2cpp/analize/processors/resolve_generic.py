from py2cpp.analize.symbol import SymbolRaw, SymbolRaws
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class ResolveGeneric:
	"""Genericのシンボルを解決"""

	@injectable
	def __call__(self, modules: Modules, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		update_raws: SymbolRaws = {}
		for key, raw in raws.items():
			fore_type = self.__analyze_fore_type(raw)
			if isinstance(fore_type, defs.GenericType):
				update_raws[key] = self.__expand_generic(raws, raw, fore_type)

		return {**raws, **update_raws}

	def __analyze_fore_type(self, raw: SymbolRaw) -> defs.Type | defs.ClassDef | None:
		if isinstance(raw.decl, (defs.AnnoAssign, defs.Catch)):
			return raw.decl.var_type
		elif isinstance(raw.decl, defs.Parameter):
			if isinstance(raw.decl.symbol, defs.DeclClassParam):
				return raw.decl.symbol.class_types.as_a(defs.ClassDef)
			elif isinstance(raw.decl.symbol, defs.DeclThisParam):
				return raw.decl.symbol.class_types.as_a(defs.ClassDef)
			else:
				return raw.decl.var_type.as_a(defs.Type)
		elif isinstance(raw.decl, (defs.MoveAssign, defs.For)):
			# 型指定が無いため全てUnknown
			return None

	def __expand_generic(self, raws: SymbolRaws, via: SymbolRaw, generic_type: defs.GenericType) -> SymbolRaw:
			attrs: list[SymbolRaw] = []
			for t_type in generic_type.template_types:
				t_raw = self.__resolve_raw(raws, t_type)
				if isinstance(t_raw.types, defs.GenericType):
					attrs.append(self.__expand_generic(raws, t_raw, t_raw.types))
				else:
					attrs.append(t_raw)

			return via.extends(*attrs)

	def __resolve_raw(self, raws: SymbolRaws, domain_type: defs.Type) -> SymbolRaw:
		scopes = [DSN.left(domain_type.scope, DSN.elem_counts(domain_type.scope) - i) for i in range(DSN.elem_counts(domain_type.scope))]
		candidates = [DSN.join(scope, domain_type.domain_name) for scope in scopes]
		for candidate in candidates:
			if candidate in raws:
				return raws[candidate]
		
		raise LogicError(f'Unresolve type. type: {domain_type.fullyname}, candidates: {candidates}')
