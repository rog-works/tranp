from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'tests')]), Tree(Token('RULE', 'name'), [Token('NAME', 'unit')]), Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'symbol')]), Tree(Token('RULE', 'name'), [Token('NAME', 'fixtures')]), Tree(Token('RULE', 'name'), [Token('NAME', 'test_db_xyz')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Z')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'A')]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Z')])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 's')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])]), Tree(Token('RULE', 'string'), [Token('STRING', "''")])])])])])])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'B')]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'B2')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])]), Tree(Token('RULE', 'string'), [Token('STRING', "''")])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_none', [])]), Tree(Token('RULE', 'block'), [Tree('funccall', [Tree('getattr', [Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'super')])]), None]), Tree(Token('RULE', 'name'), [Token('NAME', '__init__')])]), None]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree('list', [])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func1')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'b')]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('const_false', [])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'b')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'B')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B2')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree(Token('RULE', 'string'), [Token('STRING', "'b.b2.v'")])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'x')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'nx')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])]), Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 's')])])])])])])])])])])
# ==========
# file_input
#   import_stmt
#     dotted_name
#       name	tests
#       name	unit
#       name	py2cpp
#       name	symbol
#       name	fixtures
#       name	test_db_xyz
#     import_names
#       name	Z
#   assign_stmt
#     anno_assign
#       var
#         name	v
#       typed_var
#         name	int
#       number	0
#   class_def
#     None
#     class_def_raw
#       name	A
#       arguments
#         argvalue
#           var
#             name	Z
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
#             return_type
#               typed_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	s
#                   typed_var
#                     name	str
#                   string	''
#   class_def
#     None
#     class_def_raw
#       name	B
#       arguments
#         argvalue
#           var
#             name	A
#       block
#         class_def
#           None
#           class_def_raw
#             name	B2
#             None
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	v
#                   typed_var
#                     name	str
#                   string	''
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
#             return_type
#               typed_none
#             block
#               funccall
#                 getattr
#                   funccall
#                     var
#                       name	super
#                     None
#                   name	__init__
#                 None
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	v
#                   typed_getitem
#                     typed_var
#                       name	list
#                     typed_slices
#                       typed_slice
#                         typed_var
#                           name	int
#                   list
#         function_def
#           None
#           function_def_raw
#             name	func1
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	b
#                   typed_getitem
#                     typed_var
#                       name	list
#                     typed_slices
#                       typed_slice
#                         typed_var
#                           name	B
#                 None
#             return_type
#               typed_var
#                 name	str
#             block
#               assign_stmt
#                 assign
#                   var
#                     name	v
#                   const_false
#               funccall
#                 var
#                   name	print
#                 arguments
#                   argvalue
#                     var
#                       name	v
#               funccall
#                 var
#                   name	print
#                 arguments
#                   argvalue
#                     getattr
#                       var
#                         name	self
#                       name	v
#               funccall
#                 var
#                   name	print
#                 arguments
#                   argvalue
#                     getattr
#                       getitem
#                         var
#                           name	b
#                         slices
#                           slice
#                             number	0
#                       name	v
#               assign_stmt
#                 assign
#                   getattr
#                     getattr
#                       var
#                         name	B
#                       name	B2
#                     name	v
#                   string	'b.b2.v'
#               assign_stmt
#                 assign
#                   getattr
#                     getattr
#                       var
#                         name	self
#                       name	x
#                     name	nx
#                   number	2
#               return_stmt
#                 getattr
#                   var
#                     name	self
#                   name	s
# 