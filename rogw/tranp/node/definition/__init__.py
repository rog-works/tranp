from typing import TypeAlias

from rogw.tranp.node.definition.accessor import *
from rogw.tranp.node.definition.element import *
from rogw.tranp.node.definition.expression import *
from rogw.tranp.node.definition.general import *
from rogw.tranp.node.definition.literal import *
from rogw.tranp.node.definition.operator import *
from rogw.tranp.node.definition.primary import *
from rogw.tranp.node.definition.statement_compound import *
from rogw.tranp.node.definition.statement_simple import *
from rogw.tranp.node.definition.terminal import *

DeclVars: TypeAlias = Parameter | Declable
DeclAll: TypeAlias = Parameter | Declable | ClassDef
Symbolic: TypeAlias = Declable | Reference | Type | Literal | ClassDef
RefAll: TypeAlias = Reference | Indexer | FuncCall
Generized: TypeAlias = Type | Literal | ClassDef
