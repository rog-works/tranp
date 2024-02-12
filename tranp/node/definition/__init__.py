from typing import TypeAlias

from tranp.node.definition.accessor import *
from tranp.node.definition.element import *
from tranp.node.definition.expression import *
from tranp.node.definition.general import *
from tranp.node.definition.literal import *
from tranp.node.definition.operator import *
from tranp.node.definition.primary import *
from tranp.node.definition.statement_compound import *
from tranp.node.definition.statement_simple import *
from tranp.node.definition.terminal import *

DeclVars: TypeAlias = Parameter | AnnoAssign | MoveAssign | For | Catch
DeclAll: TypeAlias = Parameter | AnnoAssign | MoveAssign | For | Catch | ClassDef
Symbolic: TypeAlias = Declable | Reference | Type | Literal | ClassDef
RefAll: TypeAlias = Reference | Indexer | FuncCall
Generized: TypeAlias = Type | Literal | ClassDef
