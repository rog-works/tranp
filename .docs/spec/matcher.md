entrypoint: render
else_if: render
else: render
if: render
while: render
for:
  func_call: .iterator is FuncCall -> .iterator
  var: func_call.calls is Var -> func_call.calls
  relay: func_call.calls is Relay -> func_call.calls

  var == 'range' -> render, 'range'
  var == 'enumerate' -> render, 'enumerate'
  relay.prop == 'items' -> render, 'dict_items'
  -> render
catch: render
try: render
with_entry: raise
with: raise
function: render
class_method: render
constructor: render
method: render
closure: render
class: render
enum: render
alt_class: render
parameter: render
decorator: render
move_assign:
  .receivers > 1 -> render, 'destruction'
  -> render
anno_assign: render
aug_assign: render
delete:
  .targets all of Indexer -> render
  -> raise
return: render
yield: render
throw: render
pass: render
break: render
continue: render
comment: render
import: render
argument: render
inherit_argument: render
argument_label: render
decl_class_var: render
decl_this_var_forward: render
decl_this_var: render
decl_local_var: render
decl_class_param: render
decl_this_param: render
types_name: render
import_name: render
import_as_name: render
relay:
  relay_receiver: .receiver is Relay -> .receiver
  cvar_relay: relay_receiver.prop == 'on' -> .
  cvar_to_raw: .prop == 'raw' -> .
  cvar_to_ref: .prop == 'ref' -> .
  cvar_to_addr: .prop == 'addr' -> .
  cvar_to_const: .prop == 'const' -> .

  cvar_relay -> render, 'cvar_relay'
  cvar_to_raw -> render, 'cvar_to_raw'
  cvar_to_ref -> render, 'cvar_to_ref'
  cvar_to_addr -> render, 'cvar_to_addr'
  cvar_to_const -> render, 'cvar_to_const'
  .prop == '__module__' -> render, '__module__'
  .prop == '__name__' -> render, '__name__'
  -> render
var:
  .@*.decl is ClassDef -> render, 'class'
  -> render
class_ref: render
this_ref: render
indexer:
  slice: .sliced -> .
  relay_receiver: .receiver is Relay -> .receiver
  cvar_relay: relay_receiver.prop == 'on' -> .
  cvar: .receiver in [...] -> .
  @**receiver: .receiver.@**

  slice && @**receiver is str -> render, 'slice_string'
  slice -> render, 'slice_array'
  cvar -> render, 'cvar'
  .@ is type -> render, 'class'
  @**receiver is tuple -> render, 'tuple'
  -> render
relay_of_type: render
var_of_type: render
dict_type: render
list_type: render
callable_type: raise
custom_type: render
union_type:
  ok1: .or_types == 2
  ok2: .or_types[0] != .or_types[1]
  ok3: NullType in .or_types
  ok4: .or_types[0] == 'CP' || .or_types[1] == 'CP'

  ok1 && ok2 && ok3 && ok4 -> render
  -> raise
null_type: render
func_call:
  var: .calls is Var -> .calls
  relay: .calls is Relay -> .calls

  var ->
    cast: var in ['int', 'float', 'bool', 'str'] -> var
    cvar: var in [...] -> var

    cast ->
      @from: .arguments[0].@
      to: var

      @from is str && to == 'str' -> render, 'cast_str_to_str'
      @from is str -> render, 'cast_str_to_bin'
      to == 'str' -> render, 'cast_bin_to_str'
      -> render, 'cast_bin_to_bin'
    cvar -> render, 'to_cvar_xxx'
  relay ->
    seq_op: relay.prop in ['pop', 'insert', 'extend', 'keys', 'values'] -> relay.prop
    format: relay.prop == 'format' -> relay.prop

    seq_op ->
      @context: relay.@.context
    format ->
      relay.receiver is String -> render, 'str_format'
      relay.@.context is str -> render, 'str_format'
    relay.prop == 'empty' -> render, 'cvar_sp_empty'
    relay.prop == 'new' ->
      @**context: relay.@.context.**
      @**context.types == 'CP' -> render, 'new_cvar_p'
      @**context.types == 'CSP' -> render, 'new_cvar_sp_list'
  var || relay ->
    .calls.@** is Enum -> render, 'cast_enum'
  -> render
