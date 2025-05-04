Transpiler Spec
===

```yaml
type: object
title: statement definitions
properties:
  class:
    type: object
    properties:
      decorators:
        type: array
        items: $ref: '#/rules/decorator'
      name: $ref: '#/terminals/name'
      parents:
        type: array
        items: $ref: '#/rules/symbol'
      statements:
        type: array
        items: $ref: '#/rules/statement'
  function:
    type: object
    properties:
      decorators:
        type: array
        items: $ref: '#/rules/decorator'
      name: $ref: '#/terminals/name'
      paramerters:
        type: array
        items: $ref: '#/rules/parameter'
      return: $ref: '#/rules/symbol'
      docstring: $ref: '#/rules/function_comment'
      statements:
        type: array
        items: $ref: '#/rules/statement'
  enum:
    type: object
    properties:
      name: $ref: '#/terminals/name'
      values: $ref: '#/structures/key_value_pair'
  list:
    type: array
    items:
      $ref: '#/rules/expression'
  dict:
    $ref: '#/structures/key_value_pair'

rules:
  # statement
  statement:
    type: object
    properties:
      # simple statement
      expression: $ref: '#/rules/expression'
      assign_stmt: $ref: '#/rules/assign_stmt'
      return_stmt: $ref: '#/rules/return_stmt'
      import_stmt: $ref: '#/rules/import_stmt'
      raise_stmt: $ref: '#/rules/raise_stmt'
      pass_stmt: $ref: '#/rules/pass_stmt'
      break_stmt: $ref: '#/rules/break_stmt'
      continue_stmt: $ref: '#/rules/continue_stmt'
      # compound statement
      function_def: $ref: '#/rules/function_def'
      class_def: $ref: '#/rules/class_def'
      if_stmt: $ref: '#/rules/if_stmt'
      for_stmt: $ref: '#/rules/for_stmt'
      while_stmt: $ref: '#/rules/while_stmt'
      try_stmt: $ref: '#/rules/try_stmt'
  # compound statement
  function_def:
    type: object
    properties:
      decorators:
        type: array
        items: $ref: '#/rules/decorator'
      name: $ref: '#/terminals/name'
      block: $ref: '#/rules/block'
  class_def:
    type: object
    properties:
      decorators:
        type: array
        items: $ref: '#/rules/decorator'
      name: $ref: '#/terminals/name'
      parents:
        type: array
        items: $ref: '#/rules/symbol'
      block: $ref: '#/rules/block'
  block:
    type: object
    properties:
      new_line: $ref: '#/terminals/new_line'
      indent: $ref: '#/terminals/indent'
      statements:
        type: array
        items: $ref: '#/rules/statement'
      dedent: $ref: '#/terminals/dedent'
  # simple statement
  if_stmt:
    type: object
    properties:
      expression: $ref: '#/rules/expression'
      block: $ref: '#/rules/block'
      elif_clauses:
        type: array
        items: $ref: '#/rules/elif'
      else:
        type: object
        properties:
          block: $ref: '#/rules/block'
  elif:
    type: object
    properties:
      expression: $ref: '#/rules/expression'
      block: $ref: '#/rules/block'
  for_stmt:
    type: object
    properties:
      name: $ref: '#/rules/var'
      expression: $ref: '#/rules/expression'
      block: $ref: '#/rules/block'
  while_stmt:
    type: object
    properties:
      expression: $ref: '#/rules/expression'
      block: $ref: '#/rules/block'
  try_stmt:
    type: object
    properties:
      block: $ref: '#/rules/block'
      except_clauses: $ref: '#/rules/except_clause'
  except_clause:
    type: object
    properties:
      symbol: $ref: '#/rules/symbol'
      alias: $ref: '#/rules/var'
      block: $ref: '#/rules/block'
  # decorator
  decorator:
    type: object
    properties:
      name: $ref: '#/terminals/name'
      arguments:
        type: array
        items: $ref: '#/terminals/symbol'
  # parameter
  parameter:
    type: object
    properties:
      name: $ref: '#/rules/var'
      type: $ref: '#/rules/symbol'
      default: $ref: '#/rules/expression'
  # argument
  argument:
    $ref: '#/rule/expression'
  # expression
  expression:
    type: string
  ternary_test:
    type: object
    properties:
      then: $ref: '#/rules/expression' # FIXME -> or_test
      cond: $ref: '#/rules/expression' # FIXME -> or_test
      else: $ref: '#/rules/expression'
  # atom
  symbol:
    type: string
    pattern: ${#/terminals/name/pattern}(\.${#/terminals/name/pattern})*
  var:
    $ref: '#/terminals/name'
  const_true:
    const: 'True'
  const_false:
    const: 'False'
  const_none:
    const: 'None'
  string:
    $ref: '#/terminals/string'
  number:
    $ref: '#/terminals/number'
  group_expr:
    type: object
    properties:
      lparen: const: (
      expression: $ref: '#/rules/expression'
      rparen: const: )
    $ref: '#/terminals/number'
  list: $ref: '#/rules/_exprlist'
  dict: $ref: '#/rules/_dict_exprlist'
  _exprlist:
    type: array
    items: $ref: '#/rules/expression'
  _dict_exprlist:
    type: array
    items: $ref: '#/rules/key_value'
  key_value:
    type: object
    properties:
      key: $ref: '#/rules/expression'
      value: $ref: '#/rules/expression'

terminals:
  name:
    type: string
    pattern: [^\W\d]\w*
  string:
    type: string
    pattern: '' # FIXME
  new_line:
    type: string
  indent:
    type: string
  dedent:
    type: string

structures:
  key_value_pair:
    type: object
    additionalProperties:
      '${#/rules/symbol/pattern}':
        type: string
```
