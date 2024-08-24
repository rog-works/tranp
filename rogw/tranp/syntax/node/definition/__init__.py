from typing import TypeAlias

from rogw.tranp.syntax.node.definition.accessible import to_accessor, PythonClassOperations
from rogw.tranp.syntax.node.definition.element import Decorator, Parameter
from rogw.tranp.syntax.node.definition.expression import Expander, Group
from rogw.tranp.syntax.node.definition.general import Entrypoint
from rogw.tranp.syntax.node.definition.literal import (
	Literal,
	# number
	Number,
	Integer,
	Float,
	# string
	DocString,
	String,
	# bool
	Boolean,
	Truthy,
	Falsy,
	# collection
	Dict,
	List,
	Pair,
	Tuple,
	# null
	Null,
)
from rogw.tranp.syntax.node.definition.operator import (
	Operator,
	# unary
	UnaryOperator,
	Factor,
	NotCompare,
	# binary
	BinaryOperator,
	# binary - comparison
	Comparison,
	OrCompare,
	AndCompare,
	OrBitwise,
	XorBitwise,
	AndBitwise,
	ShiftBitwise,
	# binary - arthmetic
	Sum,
	Term,
	# tenary
	TenaryOperator,
)
from rogw.tranp.syntax.node.definition.primary import (
	# argument
	Argument,
	InheritArgument,
	ArgumentLabel,
	# declable
	Declable,
	DeclVar,
	DeclClassVar,
	DeclThisVarForward,
	DeclThisVar,
	# declable - local
	DeclLocalVar,
	DeclParam,
	DeclClassParam,
	DeclThisParam,
	# declable - name
	DeclName,
	TypesName,
	AltTypesName,
	ImportName,
	ImportAsName,
	# reference
	Reference,
	Relay,
	Var,
	ClassRef,
	ThisRef,
	Indexer,
	# path
	Path,
	ImportPath,
	DecoratorPath,
	# type
	Type,
	GeneralType,
	RelayOfType,
	VarOfType,
	# type - generic
	GenericType,
	ListType,
	DictType,
	CallableType,
	CustomType,
	# type - other
	UnionType,
	NullType,
	TypeParameters,
	# func call
	FuncCall,
	Super,
	# other
	Elipsis,
	# generator
	CompFor,
	Generator,
	Comprehension,
	ListComp,
	DictComp,
)
from rogw.tranp.syntax.node.definition.statement_compound import (
	Block,
	# flow
	Flow,
	FlowEnter,
	FlowPart,
	IfClause,
	ElseIf,
	Else,
	If,
	While,
	ForIn,
	For,
	Catch,
	TryClause,
	Try,
	WithEntry,
	With,
	# class
	ClassDef,
	# class - function
	Function,
	ClassMethod,
	Constructor,
	Method,
	Closure,
	# class - class
	Class,
	Enum,
	AltClass,
	TemplateClass,
	# utility
	VarsCollector,
)
from rogw.tranp.syntax.node.definition.statement_simple import (
	# assign
	Assign,
	MoveAssign,
	AnnoAssign,
	AugAssign,
	Delete,
	# flow
	Return,
	Yield,
	Throw,
	Pass,
	Break,
	Continue,
	# comment
	Comment,
	# import
	Import,
)
from rogw.tranp.syntax.node.definition.terminal import Terminal, Empty

DeclVars: TypeAlias = Parameter | Declable
DeclAll: TypeAlias = Parameter | Declable | ClassDef
Symbolic: TypeAlias = Declable | Relay | Var | Type | Literal | ClassDef
ClassOrType: TypeAlias = Class | AltClass | TemplateClass | Type

# XXX 上記のTypeAliasは実引数に指定できないため、等価なtupleを定義
DeclVarsTs = Parameter, Declable
DeclAllTs = Parameter, Declable, ClassDef
SymbolicTs = Declable, Relay, Var, Type, Literal, ClassDef
ClassOrTypeTs = Class, AltClass, TemplateClass, Type
