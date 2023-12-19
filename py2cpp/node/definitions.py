import py2cpp.node.definition as defs
from py2cpp.node.nodes import Settings


def make_settings() -> Settings:
	return Settings(
		symbols={
			# -- General --
			'file_input': defs.FileInput,
			# -- Statement compound --
			'if_stmt': defs.If,
			'function_def': defs.Function,
			'class_def': defs.Class,
			'enum_def': defs.Enum,
			# -- Function/Class Elements --
			'paramvalue': defs.Parameter,
			# '': defs.Var
			'block': defs.Block,
			'decorator': defs.Decorator,
			# -- Statement simple --
			'assign_stmt': defs.Assign,
			'return_stmt': defs.Return,
			'import_stmt': defs.Import,
			# -- Primary --
			'getattr': defs.Symbol,
			# 'getattr': defs.Self,
			'getitem': defs.GetItem,
			# 'getitem': defs.Indexer,
			# 'getitem': defs.ListType,
			# 'getitem': defs.DictType,
			'funccall': defs.FuncCall,
			# -- Common --
			'argvalue': defs.Argument,
			# -- Operator --
			# 'unary_op': defs.UnaryOperator
			# 'binary_op': defs.BinaryOperator
			# 'group_expr': defs.Group
			# -- Literal --
			'number': defs.Number,
			# 'number': defs.Integer,
			# 'number': defs.Float,
			'string': defs.String,
			# 'key_value': defs.KeyValue
			'list': defs.List,
			'dict': defs.Dict,
			# -- Expression --
			# 'expression': defs.Expression
			# -- Terminal --
			# '': defs.Terminal
			'const_none': defs.Null,
			'__empty__': defs.Empty,
		},
		fallback=defs.Terminal
	)
