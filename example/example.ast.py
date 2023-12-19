from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'directive')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'enum')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CEnum')])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'string'), [Token('STRING', "'once'")])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'x')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'y')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'z')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])])]), None])]), Tree('const_none', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'x')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'y')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'z')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('const_none', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '3')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '4')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '5')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Max')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '6')])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'fromCell')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '100')])])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Tree(Token('RULE', 'term'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])]), Token('STAR', '*'), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'unit')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'y')])])])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'float')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'cell')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'z')])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Vector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fx')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fy')])])]), Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'fz')])])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'classmethod')])]), None])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndexToVector')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'cls')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'dict')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])])]), Tree(Token('RULE', 'slice'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])])])])]), Tree('dict', [Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Left')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Right')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Back')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Front')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Bottom')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'factor'), [Token('MINUS', '-'), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Top')])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'IntVector')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree('funccall', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'CellMesh')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'FaceIndexs')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'faceIndex')])])])])])])])])])])])])])])])])
# ==========
# file_input
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	directive
#     import_names
#       name	pragma
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	enum
#     import_names
#       name	CEnum
#   funccall
#     var
#       name	pragma
#     arguments
#       argvalue
#         string	'once'
#   class_def
#     None
#     class_def_raw
#       name	Vector
#       None
#       block
#         function_def
#           None
#           function_def_raw
#             name	__init__
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	x
#                   var
#                     name	float
#                 None
#               paramvalue
#                 typedparam
#                   name	y
#                   var
#                     name	float
#                 None
#               paramvalue
#                 typedparam
#                   name	z
#                   var
#                     name	float
#                 None
#             const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	x
#                   var
#                     name	float
#                   var
#                     name	x
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	y
#                   var
#                     name	float
#                   var
#                     name	y
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	z
#                   var
#                     name	float
#                   var
#                     name	z
#   class_def
#     None
#     class_def_raw
#       name	IntVector
#       None
#       block
#         function_def
#           None
#           function_def_raw
#             name	__init__
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	x
#                   var
#                     name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	y
#                   var
#                     name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	z
#                   var
#                     name	int
#                 None
#             const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	x
#                   var
#                     name	int
#                   var
#                     name	x
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	y
#                   var
#                     name	int
#                   var
#                     name	y
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	z
#                   var
#                     name	int
#                   var
#                     name	z
#   class_def
#     None
#     class_def_raw
#       name	CellMesh
#       None
#       block
#         enum_def
#           name	FaceIndexs
#           block
#             assign_stmt
#               assign
#                 var
#                   name	Left
#                 number	0
#             assign_stmt
#               assign
#                 var
#                   name	Right
#                 number	1
#             assign_stmt
#               assign
#                 var
#                   name	Back
#                 number	2
#             assign_stmt
#               assign
#                 var
#                   name	Front
#                 number	3
#             assign_stmt
#               assign
#                 var
#                   name	Bottom
#                 number	4
#             assign_stmt
#               assign
#                 var
#                   name	Top
#                 number	5
#             assign_stmt
#               assign
#                 var
#                   name	Max
#                 number	6
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	fromCell
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	cell
#                   var
#                     name	IntVector
#                 None
#               paramvalue
#                 typedparam
#                   name	unit
#                   var
#                     name	int
#                 number	100
#             var
#               name	Vector
#             block
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	x
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	x
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	y
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	y
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   getattr
#                     var
#                       name	cell
#                     name	z
#                   term
#                     getattr
#                       var
#                         name	cell
#                       name	z
#                     *
#                     var
#                       name	unit
#               assign_stmt
#                 assign
#                   var
#                     name	fx
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	x
#               assign_stmt
#                 assign
#                   var
#                     name	fy
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	y
#               assign_stmt
#                 assign
#                   var
#                     name	fz
#                   funccall
#                     var
#                       name	float
#                     arguments
#                       argvalue
#                         getattr
#                           var
#                             name	cell
#                           name	z
#               return_stmt
#                 funccall
#                   var
#                     name	Vector
#                   arguments
#                     argvalue
#                       var
#                         name	fx
#                     argvalue
#                       var
#                         name	fy
#                     argvalue
#                       var
#                         name	fz
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	classmethod
#               None
#           function_def_raw
#             name	faceIndexToVector
#             parameters
#               paramvalue
#                 typedparam
#                   name	cls
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	faceIndex
#                   var
#                     name	int
#                 None
#             var
#               name	IntVector
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	map
#                   getitem
#                     var
#                       name	dict
#                     slices
#                       slice
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                       slice
#                         var
#                           name	IntVector
#                   dict
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Left
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             factor
#                               -
#                               number	1
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Right
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	1
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Back
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             factor
#                               -
#                               number	1
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Front
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	1
#                           argvalue
#                             number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Bottom
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                           argvalue
#                             factor
#                               -
#                               number	1
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         name	Top
#                       funccall
#                         var
#                           name	IntVector
#                         arguments
#                           argvalue
#                             number	0
#                           argvalue
#                             number	0
#                           argvalue
#                             number	1
#               return_stmt
#                 getitem
#                   var
#                     name	map
#                   slices
#                     slice
#                       funccall
#                         getattr
#                           var
#                             name	CellMesh
#                           name	FaceIndexs
#                         arguments
#                           argvalue
#                             var
#                               name	faceIndex
# 