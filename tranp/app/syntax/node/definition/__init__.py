from typing import TypeAlias

from tranp.app.syntax.node.definition.accessible import PythonClassOperations, to_accessor
from tranp.app.syntax.node.definition.element import Decorator, Parameter
from tranp.app.syntax.node.definition.expression import Group, Spread
from tranp.app.syntax.node.definition.general import Entrypoint
from tranp.app.syntax.node.definition.literal import (
	# bool
	Boolean,
	# collection
	Dict,
	# string
	DocString,
	Falsy,
	Float,
	Integer,
	List,
	Literal,
	# null
	Null,
	# number
	Number,
	Pair,
	String,
	Truthy,
	Tuple,
)
from tranp.app.syntax.node.definition.operator import (
	AndBitwise,
	AndCompare,
	# binary
	BinaryOperator,
	# binary - comparison
	Comparison,
	Factor,
	NotCompare,
	Operator,
	OrBitwise,
	OrCompare,
	ShiftBitwise,
	# binary - arthmetic
	Sum,
	Term,
	# ternary
	TernaryOperator,
	# unary
	UnaryOperator,
	XorBitwise,
)
from tranp.app.syntax.node.definition.primary import (
	AltTypesName,
	# argument
	Argument,
	ArgumentLabel,
	CallableType,
	ClassRef,
	# generator
	CompFor,
	Comprehension,
	CustomType,
	# declable
	Declable,
	DeclClassParam,
	DeclClassVar,
	# declable - local
	DeclLocalVar,
	# declable - name
	DeclName,
	DeclParam,
	DeclThisParam,
	DeclThisVar,
	DeclThisVarForward,
	DeclVar,
	DecoratorPath,
	DictComp,
	DictType,
	# other
	Elipsis,
	# func call
	FuncCall,
	GeneralType,
	Generator,
	# type - generic
	GenericType,
	ImportAsName,
	ImportName,
	ImportPath,
	Indexer,
	InheritArgument,
	# labmda
	Lambda,
	ListComp,
	ListType,
	LiteralDictType,
	LiteralType,
	NullType,
	# path
	Path,
	# reference
	Reference,
	Relay,
	RelayOfType,
	Super,
	ThisRef,
	# type
	Type,
	TypeParameters,
	TypesName,
	# type - other
	UnionType,
	Var,
	VarOfType,
)
from tranp.app.syntax.node.definition.statement_compound import (
	AltClass,
	Block,
	Catch,
	# class - class
	Class,
	# class
	ClassDef,
	ClassMethod,
	Closure,
	Constructor,
	Else,
	ElseIf,
	Enum,
	# flow
	Flow,
	FlowEnter,
	FlowPart,
	For,
	ForIn,
	# class - function
	Function,
	If,
	IfClause,
	Method,
	TemplateClass,
	Try,
	TryClause,
	# utility
	VarsCollector,
	While,
	With,
	WithEntry,
)
from tranp.app.syntax.node.definition.statement_simple import (
	AnnoAssign,
	Assert,
	# assign
	Assign,
	AugAssign,
	Break,
	# comment
	Comment,
	Continue,
	Delete,
	# import
	Import,
	MoveAssign,
	Pass,
	# flow
	Return,
	Throw,
	Yield,
)
from tranp.app.syntax.node.definition.terminal import Empty, Terminal

DeclVars: TypeAlias = Parameter | Declable
DeclAll: TypeAlias = Parameter | Declable | ClassDef
DeclClasses: TypeAlias = Class | AltClass | TemplateClass
Symbolic: TypeAlias = Declable | Relay | Var | Type | Literal | ClassDef
ClassOrType: TypeAlias = Class | AltClass | TemplateClass | Type

# XXX 上記のTypeAliasは実引数に指定できないため、等価なtupleを定義
DeclVarsTs = Parameter, Declable
DeclAllTs = Parameter, Declable, ClassDef
DeclClassesTs = Class, AltClass, TemplateClass
DeclAssignTs = MoveAssign, AnnoAssign
SymbolicTs = Declable, Relay, Var, Type, Literal, ClassDef
ClassOrTypeTs = Class, AltClass, TemplateClass, Type
