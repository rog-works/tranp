from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'directive')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])])]), Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'enum')])]), Tree(Token('RULE', 'import_names'), [Tree(Token('RULE', 'name'), [Token('NAME', 'CEnum')]), Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])]), Tree('funccall', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'pragma')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'string'), [Token('STRING', "'once'")])])])]), Tree(Token('RULE', 'class_def'), [None, Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Base')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'pass_stmt'), [])])])]), Tree(Token('RULE', 'class_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'deco')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])]), Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Base')])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Values')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'B')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func1')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'value')]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'if_stmt'), [Tree(Token('RULE', 'comparison'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'value')])]), Tree(Token('RULE', 'comp_op'), [Token('__ANON_14', '==')]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])])]), Tree(Token('RULE', 'elifs'), []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'deco_func')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'string'), [Token('STRING', "'hoge'")])])])])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '_func2')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'text')]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'map')])]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'dict')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_getattr', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])])]), Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree('dict', [Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'A')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])]), Tree(Token('RULE', 'key_value'), [Tree('getattr', [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'empty_map')])]), Tree('dict', [])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'arr')])]), Tree('typed_getitem', [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'list')])]), Tree(Token('RULE', 'typed_slices'), [Tree(Token('RULE', 'typed_slice'), [Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])])]), Tree('list', [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]), Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'empty_arr')])]), Tree('list', [])])]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'arr')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'aug_assign'), [Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'arr')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'aug_assign_op'), [Token('__ANON_1', '+=')]), Tree('getitem', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'arr')])]), Tree(Token('RULE', 'slices'), [Tree(Token('RULE', 'slice'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])]), Tree(Token('RULE', 'return_stmt'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'arr')])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'v')]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 's')]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])]), Tree(Token('RULE', 'name'), [Token('NAME', 's')])]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])]), Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 's')])])])])])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func3')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'ok')]), Tree('typed_var', [Tree(Token('RULE', 'name'), [Token('NAME', 'bool')])])]), None])]), Tree(Token('RULE', 'return_type'), [Tree('typed_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'pass_stmt'), [])])])])])
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
#       name	A
#   funccall
#     var
#       name	pragma
#     arguments
#       argvalue
#         string	'once'
#   class_def
#     None
#     class_def_raw
#       name	Base
#       None
#       block
#         pass_stmt
#   class_def
#     decorators
#       decorator
#         dotted_name
#           name	deco
#         arguments
#           argvalue
#             var
#               name	A
#           argvalue
#             getattr
#               var
#                 name	A
#               name	B
#     class_def_raw
#       name	Hoge
#       arguments
#         argvalue
#           var
#             name	Base
#       block
#         enum_def
#           name	Values
#           block
#             assign_stmt
#               assign
#                 var
#                   name	A
#                 number	0
#             assign_stmt
#               assign
#                 var
#                   name	B
#                 number	1
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
#                   name	value
#                   typed_var
#                     name	int
#                 None
#             return_type
#               typed_var
#                 name	Values
#             block
#               if_stmt
#                 comparison
#                   var
#                     name	value
#                   comp_op	==
#                   number	0
#                 block
#                   return_stmt
#                     getattr
#                       getattr
#                         var
#                           name	Hoge
#                         name	Values
#                       name	A
#                 elifs
#                 block
#                   return_stmt
#                     getattr
#                       getattr
#                         var
#                           name	Hoge
#                         name	Values
#                       name	B
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	deco_func
#               arguments
#                 argvalue
#                   string	'hoge'
#           function_def_raw
#             name	_func2
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	text
#                   typed_var
#                     name	str
#                 None
#             return_type
#               typed_getitem
#                 typed_var
#                   name	list
#                 typed_slices
#                   typed_slice
#                     typed_var
#                       name	int
#             block
#               assign_stmt
#                 anno_assign
#                   var
#                     name	map
#                   typed_getitem
#                     typed_var
#                       name	dict
#                     typed_slices
#                       typed_slice
#                         typed_getattr
#                           typed_var
#                             name	Hoge
#                           name	Values
#                       typed_slice
#                         typed_var
#                           name	int
#                   dict
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	Hoge
#                           name	Values
#                         name	A
#                       number	0
#                     key_value
#                       getattr
#                         getattr
#                           var
#                             name	Hoge
#                           name	Values
#                         name	B
#                       number	1
#               assign_stmt
#                 assign
#                   var
#                     name	empty_map
#                   dict
#               assign_stmt
#                 anno_assign
#                   var
#                     name	arr
#                   typed_getitem
#                     typed_var
#                       name	list
#                     typed_slices
#                       typed_slice
#                         typed_var
#                           name	int
#                   list
#                     number	0
#                     number	1
#                     number	2
#               assign_stmt
#                 assign
#                   var
#                     name	empty_arr
#                   list
#               getitem
#                 var
#                   name	arr
#                 slices
#                   slice
#                     number	0
#               assign_stmt
#                 aug_assign
#                   getitem
#                     var
#                       name	arr
#                     slices
#                       slice
#                         number	0
#                   aug_assign_op	+=
#                   getitem
#                     var
#                       name	arr
#                     slices
#                       slice
#                         number	1
#               return_stmt
#                 var
#                   name	arr
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
#                   name	v
#                   typed_var
#                     name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	s
#                   typed_var
#                     name	str
#                 None
#             return_type
#               typed_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	v
#                   typed_var
#                     name	int
#                   var
#                     name	v
#               assign_stmt
#                 anno_assign
#                   getattr
#                     var
#                       name	self
#                     name	s
#                   typed_var
#                     name	str
#                   var
#                     name	s
#   function_def
#     None
#     function_def_raw
#       name	func3
#       parameters
#         paramvalue
#           typedparam
#             name	ok
#             typed_var
#               name	bool
#           None
#       return_type
#         typed_none
#       block
#         pass_stmt
# 