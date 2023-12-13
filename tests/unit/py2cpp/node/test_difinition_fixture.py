from lark import Tree, Token
def fixture() -> Tree:
	return Tree(Token('RULE', 'file_input'), [Tree(Token('RULE', 'import_stmt'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'py2cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'cpp')]), Tree(Token('RULE', 'name'), [Token('NAME', 'enum')])])]), Tree(Token('RULE', 'class_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'deco')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])])]), Tree(Token('RULE', 'argvalue'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])]), Tree(Token('RULE', 'class_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')]), None, Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'enum_def'), [Tree(Token('RULE', 'name'), [Token('NAME', 'Values')]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'assign'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')])])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func1')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'value')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'if_stmt'), [Tree(Token('RULE', 'comparison'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'value')])])]), Tree(Token('RULE', 'comp_op'), [Token('__ANON_14', '==')]), Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '0')])])])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'A')])])])]), Tree(Token('RULE', 'elifs'), []), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'return_stmt'), [Tree('getattr', [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'Hoge')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'Values')])]), Tree(Token('RULE', 'name'), [Token('NAME', 'B')])])])])])])])]), Tree(Token('RULE', 'function_def'), [Tree(Token('RULE', 'decorators'), [Tree(Token('RULE', 'decorator'), [Tree(Token('RULE', 'dotted_name'), [Tree(Token('RULE', 'name'), [Token('NAME', 'deco_func')])]), Tree(Token('RULE', 'arguments'), [Tree(Token('RULE', 'argvalue'), [Tree(Token('RULE', 'primary'), [Tree(Token('RULE', 'atom'), [Tree(Token('RULE', 'string'), [Token('STRING', "'hoge'")])])])])])])]), Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func2')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'text')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('const_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'if_stmt'), [Tree(Token('RULE', 'primary'), [Tree('const_false', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'b')])])])]), Tree(Token('RULE', 'elifs'), []), None])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', '__init__')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'self')]), None]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'v')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])])]), None]), Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 's')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('const_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 'v')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'int')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'v')])])])])]), Tree(Token('RULE', 'assign_stmt'), [Tree(Token('RULE', 'anno_assign'), [Tree('getattr', [Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'self')])])]), Tree(Token('RULE', 'name'), [Token('NAME', 's')])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'str')])])]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 's')])])])])])])])])])])]), Tree(Token('RULE', 'function_def'), [None, Tree(Token('RULE', 'function_def_raw'), [Tree(Token('RULE', 'name'), [Token('NAME', 'func3')]), Tree(Token('RULE', 'parameters'), [Tree(Token('RULE', 'paramvalue'), [Tree(Token('RULE', 'typedparam'), [Tree(Token('RULE', 'name'), [Token('NAME', 'ok')]), Tree(Token('RULE', 'primary'), [Tree('var', [Tree(Token('RULE', 'name'), [Token('NAME', 'bool')])])])]), None])]), Tree(Token('RULE', 'primary'), [Tree('const_none', [])]), Tree(Token('RULE', 'block'), [Tree(Token('RULE', 'pass_stmt'), [])])])])])
# ==========
# file_input
#   import_stmt
#     dotted_name
#       name	py2cpp
#       name	cpp
#       name	enum
#   class_def
#     decorators
#       decorator
#         dotted_name
#           name	deco
#         arguments
#           argvalue
#             primary
#               var
#                 name	A
#           argvalue
#             getattr
#               primary
#                 var
#                   name	A
#               name	B
#     class_def_raw
#       name	Hoge
#       None
#       block
#         enum_def
#           name	Values
#           block
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	A
#                 primary
#                   atom
#                     number	0
#             assign_stmt
#               assign
#                 primary
#                   var
#                     name	B
#                 primary
#                   atom
#                     number	1
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
#                   primary
#                     var
#                       name	int
#                 None
#             primary
#               var
#                 name	Values
#             block
#               if_stmt
#                 comparison
#                   primary
#                     var
#                       name	value
#                   comp_op	==
#                   primary
#                     atom
#                       number	0
#                 block
#                   return_stmt
#                     getattr
#                       getattr
#                         primary
#                           var
#                             name	Hoge
#                         name	Values
#                       name	A
#                 elifs
#                 block
#                   return_stmt
#                     getattr
#                       getattr
#                         primary
#                           var
#                             name	Hoge
#                         name	Values
#                       name	B
#         function_def
#           decorators
#             decorator
#               dotted_name
#                 name	deco_func
#               arguments
#                 argvalue
#                   primary
#                     atom
#                       string	'hoge'
#           function_def_raw
#             name	func2
#             parameters
#               paramvalue
#                 typedparam
#                   name	self
#                   None
#                 None
#               paramvalue
#                 typedparam
#                   name	text
#                   primary
#                     var
#                       name	str
#                 None
#             primary
#               const_none
#             block
#               if_stmt
#                 primary
#                   const_false
#                 block
#                   primary
#                     var
#                       name	b
#                 elifs
#                 None
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
#                   primary
#                     var
#                       name	int
#                 None
#               paramvalue
#                 typedparam
#                   name	s
#                   primary
#                     var
#                       name	str
#                 None
#             primary
#               const_none
#             block
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	v
#                   primary
#                     var
#                       name	int
#                   primary
#                     var
#                       name	v
#               assign_stmt
#                 anno_assign
#                   getattr
#                     primary
#                       var
#                         name	self
#                     name	s
#                   primary
#                     var
#                       name	str
#                   primary
#                     var
#                       name	s
#   function_def
#     None
#     function_def_raw
#       name	func3
#       parameters
#         paramvalue
#           typedparam
#             name	ok
#             primary
#               var
#                 name	bool
#           None
#       primary
#         const_none
#       block
#         pass_stmt
# 