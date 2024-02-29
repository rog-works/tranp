from typing import TypeAlias

from rogw.tranp.node.definition.accessor import to_access
from rogw.tranp.node.definition.element import Decorator, Parameter
from rogw.tranp.node.definition.expression import Group
from rogw.tranp.node.definition.general import Entrypoint
from rogw.tranp.node.definition.literal import (
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
	# null
	Null,
)
from rogw.tranp.node.definition.operator import (
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
from rogw.tranp.node.definition.primary import (
	Fragment,
	# declable
	Declable,
	DeclVar,
	DeclClassVar,
	DeclThisVar,
	# declable - local
	DeclLocalVar,
	DeclParam,
	DeclClassParam,
	DeclThisParam,
	# declable - name
	DeclName,
	TypesName,
	ImportName,
	# reference
	Reference,
	Relay,
	Var,
	ClassRef,
	ThisRef,
	ArgumentLabel,
	Variable,
	# path
	Path,
	ImportPath,
	DecoratorPath,
	# indexer
	Indexer,
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
	# argument
	Argument,
	InheritArgument,
	# other
	Elipsis,
	# generator
	CompFor,
	Generator,
	Comprehension,
	ListComp,
	DictComp,
)
from rogw.tranp.node.definition.statement_compound import (
	Block,
	# flow
	Flow,
	FlowEnter,
	FlowPart,
	ElseIf,
	If,
	While,
	ForIn,
	For,
	Catch,
	Try,
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
	ClassSymbolMaker,
)
from rogw.tranp.node.definition.statement_simple import (
	# assign
	Assign,
	MoveAssign,
	AnnoAssign,
	AugAssign,
	# flow
	Return,
	Throw,
	Pass,
	Break,
	Continue,
	# comment
	Comment,
	# import
	Import,
)
from rogw.tranp.node.definition.terminal import Terminal, Empty

DeclVars: TypeAlias = Parameter | Declable
DeclAll: TypeAlias = Parameter | Declable | ClassDef
Symbolic: TypeAlias = Declable | Reference | Type | Literal | ClassDef
RefAll: TypeAlias = Reference | Indexer | FuncCall
Generized: TypeAlias = Type | Literal | ClassDef
