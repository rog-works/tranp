from py2cpp.ast.query import Query
from py2cpp.ast.resolver import SymbolMapping
import py2cpp.node.definition as defs
from py2cpp.node.node import Node


def entrypoint(query: Query[Node]) -> Node:
	return query.by('file_input')


def symbol_mapping() -> SymbolMapping:
	return SymbolMapping(
		symbols={
			# -- General --
			'file_input': defs.Entrypoint,
			# -- Statement compound --
			'elif_': defs.ElseIf,
			'if_stmt': defs.If,
			'while_stmt': defs.While,
			'for_stmt': defs.For,
			'except_clause': defs.Catch,
			'try_stmt': defs.Try,
			'function_def': defs.Function,
			# 'function_def': defs.ClassMethod,
			# 'function_def': defs.Constructor,
			# 'function_def': defs.Method,
			'class_def': defs.Class,
			'enum_def': defs.Enum,
			# -- Function/Class Elements --
			'paramvalue': defs.Parameter,
			'return_type': defs.ReturnType,
			'block': defs.Block,
			'decorator': defs.Decorator,
			# -- Statement simple --
			'assign_stmt': defs.Assign,
			'return_stmt': defs.Return,
			'raise_stmt': defs.Throw,
			'pass_stmt': defs.Pass,
			'break_stmt': defs.Break,
			'continue_stmt': defs.Continue,
			'import_stmt': defs.Import,
			# -- Primary --
			'getattr': defs.Fragment,
			'var': defs.Fragment,
			'name': defs.Fragment,
			# '': defs.ThisVar,
			# '': defs.LocalVar,
			'dotted_name': defs.Path,
			'getitem': defs.Indexer,
			'typed_getattr': defs.GeneralType,
			'typed_var': defs.GeneralType,
			'typed_getitem': defs.GenericType,
			# 'typed_getitem': defs.ListType,
			# 'typed_getitem': defs.DictType,
			'typed_or_expr': defs.UnionType,
			'typed_none': defs.NoneType,
			'funccall': defs.FuncCall,
			# 'funccall': defs.Super,
			# -- Common --
			'argvalue': defs.Argument,
			'typed_argvalue': defs.InheritArgument,
			# -- Operator --
			'factor': defs.Factor,
			'not_test': defs.NotCompare,
			'or_test': defs.OrCompare,
			'and_test': defs.AndCompare,
			'comparison': defs.Comparison,
			'or_expr': defs.OrBitwise,
			'xor_expr': defs.XorBitwise,
			'and_expr': defs.AndBitwise,
			'shift_expr': defs.ShiftBitwise,
			'sum': defs.Sum,
			'term': defs.Term,
			# 'group_expr': defs.Group,
			# -- Literal --
			'number': defs.Number,
			# 'number': defs.Integer,
			# 'number': defs.Float,
			'string': defs.String,
			'const_true': defs.Truthy,
			'const_false': defs.Falsy,
			'key_value': defs.Pair,
			'list': defs.List,
			'dict': defs.Dict,
			'const_none': defs.Null,
			# -- Expression --
			# 'expression': defs.Expression,
			# -- Terminal --
			# '': defs.Terminal,
			'__empty__': defs.Empty,
		},
		fallback=defs.Terminal
	)
