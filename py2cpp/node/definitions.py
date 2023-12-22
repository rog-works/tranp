import py2cpp.node.definition as defs
from py2cpp.node.nodes import Settings


def make_settings() -> Settings:
	return Settings(
		symbols={
			# -- General --
			'file_input': defs.Module,
			# -- Statement compound --
			'elif_': defs.ElseIf,
			'if_stmt': defs.If,
			'while_stmt': defs.While,
			'for_stmt': defs.For,
			'except_clause': defs.Catch,
			'try_stmt': defs.Try,
			'function_def': defs.Function,
			'class_def': defs.Class,
			'enum_def': defs.Enum,
			# -- Function/Class Elements --
			'paramvalue': defs.Parameter,
			# '': defs.Var,
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
			'getattr': defs.Symbol,
			'var': defs.Symbol,
			'name': defs.Symbol,
			'dotted_name': defs.Symbol,
			# 'getattr': defs.Self,
			'getitem': defs.GetItem,
			# 'getitem': defs.Indexer,
			# 'getitem': defs.ListType,
			# 'getitem': defs.DictType,
			# 'getitem': defs.UnionType,
			'funccall': defs.FuncCall,
			# -- Common --
			'argvalue': defs.Argument,
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
			'key_value': defs.KeyValue,
			'list': defs.List,
			'dict': defs.Dict,
			# -- Expression --
			# 'expression': defs.Expression,
			# -- Terminal --
			# '': defs.Terminal,
			'const_none': defs.Null,
			'__empty__': defs.Empty,
		},
		fallback=defs.Terminal
	)
