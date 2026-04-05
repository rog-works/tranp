from typing import TypeAlias

# String

class char(str): ...
class wchar_t(str): ...

# Number

byte: TypeAlias = int
int8: TypeAlias = int
uint8: TypeAlias = int
int32: TypeAlias = int
int64: TypeAlias = int
uint32: TypeAlias = int
uint64: TypeAlias = int
double: TypeAlias = float

# Object

# XXX 本質的には正しくないが、void*としてのみ使用するため、これによって無駄なキャストを軽減
void: TypeAlias = object
