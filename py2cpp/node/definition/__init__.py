from typing import TypeAlias

from py2cpp.node.definition.accessor import *
from py2cpp.node.definition.element import *
from py2cpp.node.definition.expression import *
from py2cpp.node.definition.general import *
from py2cpp.node.definition.literal import *
from py2cpp.node.definition.operator import *
from py2cpp.node.definition.primary import *
from py2cpp.node.definition.statement_compound import *
from py2cpp.node.definition.statement_simple import *
from py2cpp.node.definition.terminal import *

DeclVars: TypeAlias = Parameter | AnnoAssign | MoveAssign | For | Catch
DeclAll: TypeAlias = Parameter | AnnoAssign | MoveAssign | For | Catch | ClassDef
Symbolic: TypeAlias = Declable | Reference | Type | Literal | ClassDef
