from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'directive')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'string'), [Token('STRING', "'once'")])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'A')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'B')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])]), Tree(Token('RULE', 'string'), [Token('STRING', "''")])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None])]), Tree('typed_none', []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree('list', [])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func1')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'b')]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])]), None])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'bool')])]), Tree('const_false', [])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'print')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'b')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])])])])])])])
# ==========
# file_input
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	directive
#     import_names
#       name	pragma
#   funccall
#     var
#       name	pragma
#     arguments
#       argvalue
#         string	'once'
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
#       None
#       block
#         class_def
#           None
#           class_def_raw
#             name	B
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
#             typed_none
#             block
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
#             typed_var
#               name	str
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	v
#                   typed_var
#                     name	bool
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
#               return_stmt
#                 getattr
#                   getattr
#                     var
#                       name	A
#                     name	B
#                   name	v
# 