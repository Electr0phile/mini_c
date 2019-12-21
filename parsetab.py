
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "DIGIT_STRING FLOAT_STRING FOR IF INCR INTEGER PLUS PRINTF RETURN STRING TYPE TYPE TYPE VARIABLE function_list : function function_list  function_list : empty  function : TYPE VARIABLE '(' arguments ')' '{' body '}'  arguments : TYPE variable_or_pointer  arguments : TYPE variable_or_pointer ',' arguments  arguments : TYPE  arguments : TYPE ',' arguments body : line bodybody : emptyline : declarationline : assignmentline : if_clauseline : for_loop line : expr_line line : return_exprline : printf_exprdeclaration : TYPE variable_list ';' declaration : TYPE variable_list \n    variable_list : variable_or_pointer\n                  | array\n    \n    variable_list : variable_or_pointer ',' variable_list\n                  | array ',' variable_list\n    \n    assignment : variable_or_pointer '=' expr_1 ';'\n               | array '=' expr_1 ';'\n    \n    assignment : variable_or_pointer '=' error ';'\n               | array '=' error ';'\n    \n    assignment : variable_or_pointer '=' '&' VARIABLE ';'\n               | array '=' '&' VARIABLE ';'\n     return_expr : RETURN expr_1 ';'  return_expr : RETURN ';'  expr_line : expr_1 ';' \n    printf_expr : PRINTF '(' STRING  ')' ';'\n                | PRINTF '(' digit ')' ';'\n                | PRINTF '(' float ')' ';'\n\n    \n    digit : DIGIT_STRING ',' expr_1\n    \n    float : FLOAT_STRING ',' expr_1\n    \n    variable_or_pointer : '*' VARIABLE\n                        | VARIABLE\n    \n    expr_1 : expr_2 '>' expr_1\n           | expr_2 '<' expr_1\n    \n    expr_1 : expr_2\n    \n    expr_2 : expr_3 PLUS expr_2\n           | expr_3 '-' expr_2\n    \n    expr_2 : expr_3\n    \n    expr_3 : expr_4 '*' expr_3\n           | expr_4 '/' expr_3\n    \n    expr_3 : expr_4\n    \n    expr_4 : '-' expr_5\n           | expr_5\n    \n    expr_5 : variable_or_pointer INCR\n    \n    expr_5 : expr_6\n    \n    expr_6 : INTEGER\n           | variable_or_pointer\n           | function_call\n           | array\n           | '(' expr_1 ')'\n    \n    if_clause : IF '(' expr_1 ')' '{' body '}'\n    \n    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' '{' body '}'\n    \n    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' body '}'\n    \n    for_loop : FOR '(' assignment expr_1 ';' expr_1 ')' '{' body\n    function_call : VARIABLE '(' arguments_call ')'  arguments_call : expr_1  arguments_call : expr_1 ',' arguments_call  array : VARIABLE '[' expr_1 ']' empty : "
    
_lr_action_items = {'TYPE':([0,2,7,11,15,17,18,24,25,26,27,28,29,30,31,32,48,49,50,51,58,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,135,136,137,139,140,141,],[4,4,8,8,8,-37,20,20,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-3,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,20,-32,-33,-34,-57,20,20,-60,-59,-58,]),'$end':([0,1,2,3,5,58,],[-65,0,-65,-2,-1,-3,]),'VARIABLE':([4,8,12,17,18,20,22,24,25,26,27,28,29,30,31,32,38,42,48,49,50,51,52,53,59,60,62,63,64,65,67,69,70,71,72,74,75,76,77,78,85,88,90,93,105,106,107,109,110,111,113,114,121,122,124,125,126,127,128,129,130,135,136,137,139,140,141,],[6,13,17,-37,21,51,56,21,-9,-10,-11,-12,-13,-14,-15,-16,56,56,-18,-19,-20,-38,56,56,-8,56,-31,56,56,51,-30,56,56,56,56,56,56,-17,51,51,112,115,56,-29,-21,-22,-64,56,-23,-25,-24,-26,56,56,-27,-28,21,56,-32,-33,-34,-57,21,21,-60,-59,-58,]),'(':([6,17,18,21,22,24,25,26,27,28,29,30,31,32,36,37,38,39,42,48,49,50,51,52,53,56,59,60,62,63,64,67,69,70,71,72,74,75,76,90,93,105,106,107,109,110,111,113,114,121,122,124,125,126,127,128,129,130,135,136,137,139,140,141,],[7,-37,22,53,22,22,-9,-10,-11,-12,-13,-14,-15,-16,64,65,22,68,22,-18,-19,-20,-38,22,22,53,-8,22,-31,22,22,-30,22,22,22,22,22,22,-17,22,-29,-21,-22,-64,22,-23,-25,-24,-26,22,22,-27,-28,22,22,-32,-33,-34,-57,22,22,-60,-59,-58,]),')':([8,9,10,13,16,17,19,40,41,43,44,45,46,47,54,55,56,57,61,73,80,81,82,89,94,95,96,99,100,101,102,103,104,107,108,123,131,132,134,],[-6,14,-4,-38,-7,-37,-5,-41,-44,-47,-49,-51,-52,-54,82,-53,-38,-55,-50,-48,108,-62,-56,116,118,119,120,-39,-40,-42,-43,-45,-46,-64,-61,-63,-35,-36,136,]),',':([8,10,13,17,40,41,43,44,45,46,47,49,50,51,55,56,57,61,73,81,82,97,98,99,100,101,102,103,104,107,108,],[11,15,-38,-37,-41,-44,-47,-49,-51,-52,-54,77,78,-38,-53,-38,-55,-50,-48,109,-56,121,122,-39,-40,-42,-43,-45,-46,-64,-61,]),'*':([8,17,18,20,21,22,24,25,26,27,28,29,30,31,32,33,35,38,42,43,44,45,46,47,48,49,50,51,52,53,55,56,57,59,60,61,62,63,64,65,67,69,70,71,72,73,74,75,76,77,78,82,90,93,105,106,107,108,109,110,111,113,114,121,122,124,125,126,127,128,129,130,135,136,137,139,140,141,],[12,-37,12,12,-38,12,12,-9,-10,-11,-12,-13,-14,-15,-16,-53,-55,12,12,74,-49,-51,-52,-54,-18,-19,-20,-38,12,12,-53,-38,-55,-8,12,-50,-31,12,12,12,-30,12,12,12,12,-48,12,12,-17,12,12,-56,12,-29,-21,-22,-64,-61,12,-23,-25,-24,-26,12,12,-27,-28,12,12,-32,-33,-34,-57,12,12,-60,-59,-58,]),'{':([14,116,136,],[18,126,137,]),'=':([17,21,33,35,51,91,92,107,],[-37,-38,60,63,-38,60,63,-64,]),'INCR':([17,21,33,55,56,],[-37,-38,61,61,-38,]),'/':([17,21,33,35,43,44,45,46,47,55,56,57,61,73,82,107,108,],[-37,-38,-53,-55,75,-49,-51,-52,-54,-53,-38,-55,-50,-48,-56,-64,-61,]),'PLUS':([17,21,33,35,41,43,44,45,46,47,55,56,57,61,73,82,103,104,107,108,],[-37,-38,-53,-55,71,-47,-49,-51,-52,-54,-53,-38,-55,-50,-48,-56,-45,-46,-64,-61,]),'-':([17,18,21,22,24,25,26,27,28,29,30,31,32,33,35,38,41,43,44,45,46,47,48,49,50,51,52,53,55,56,57,59,60,61,62,63,64,67,69,70,71,72,73,74,75,76,82,90,93,103,104,105,106,107,108,109,110,111,113,114,121,122,124,125,126,127,128,129,130,135,136,137,139,140,141,],[-37,42,-38,42,42,-9,-10,-11,-12,-13,-14,-15,-16,-53,-55,42,72,-47,-49,-51,-52,-54,-18,-19,-20,-38,42,42,-53,-38,-55,-8,42,-50,-31,42,42,-30,42,42,42,42,-48,42,42,-17,-56,42,-29,-45,-46,-21,-22,-64,-61,42,-23,-25,-24,-26,42,42,-27,-28,42,42,-32,-33,-34,-57,42,42,-60,-59,-58,]),'>':([17,21,33,35,40,41,43,44,45,46,47,55,56,57,61,73,82,101,102,103,104,107,108,],[-37,-38,-53,-55,69,-44,-47,-49,-51,-52,-54,-53,-38,-55,-50,-48,-56,-42,-43,-45,-46,-64,-61,]),'<':([17,21,33,35,40,41,43,44,45,46,47,55,56,57,61,73,82,101,102,103,104,107,108,],[-37,-38,-53,-55,70,-44,-47,-49,-51,-52,-54,-53,-38,-55,-50,-48,-56,-42,-43,-45,-46,-64,-61,]),';':([17,21,33,34,35,38,40,41,43,44,45,46,47,48,49,50,51,55,56,57,61,66,73,82,83,84,86,87,99,100,101,102,103,104,105,106,107,108,112,115,117,118,119,120,],[-37,-38,-53,62,-55,67,-41,-44,-47,-49,-51,-52,-54,76,-19,-20,-38,-53,-38,-55,-50,93,-48,-56,110,111,113,114,-39,-40,-42,-43,-45,-46,-21,-22,-64,-61,124,125,127,128,129,130,]),'IF':([17,18,24,25,26,27,28,29,30,31,32,48,49,50,51,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,135,136,137,139,140,141,],[-37,36,36,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,36,-32,-33,-34,-57,36,36,-60,-59,-58,]),'FOR':([17,18,24,25,26,27,28,29,30,31,32,48,49,50,51,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,135,136,137,139,140,141,],[-37,37,37,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,37,-32,-33,-34,-57,37,37,-60,-59,-58,]),'RETURN':([17,18,24,25,26,27,28,29,30,31,32,48,49,50,51,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,135,136,137,139,140,141,],[-37,38,38,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,38,-32,-33,-34,-57,38,38,-60,-59,-58,]),'PRINTF':([17,18,24,25,26,27,28,29,30,31,32,48,49,50,51,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,135,136,137,139,140,141,],[-37,39,39,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,39,-32,-33,-34,-57,39,39,-60,-59,-58,]),'INTEGER':([17,18,22,24,25,26,27,28,29,30,31,32,38,42,48,49,50,51,52,53,59,60,62,63,64,67,69,70,71,72,74,75,76,90,93,105,106,107,109,110,111,113,114,121,122,124,125,126,127,128,129,130,135,136,137,139,140,141,],[-37,46,46,46,-9,-10,-11,-12,-13,-14,-15,-16,46,46,-18,-19,-20,-38,46,46,-8,46,-31,46,46,-30,46,46,46,46,46,46,-17,46,-29,-21,-22,-64,46,-23,-25,-24,-26,46,46,-27,-28,46,46,-32,-33,-34,-57,46,46,-60,-59,-58,]),'}':([17,18,23,24,25,26,27,28,29,30,31,32,48,49,50,51,59,62,67,76,93,105,106,107,110,111,113,114,124,125,126,128,129,130,133,135,136,137,138,139,140,141,],[-37,-65,58,-65,-9,-10,-11,-12,-13,-14,-15,-16,-18,-19,-20,-38,-8,-31,-30,-17,-29,-21,-22,-64,-23,-25,-24,-26,-27,-28,-65,-32,-33,-34,135,-57,-65,-65,140,141,-59,-58,]),']':([17,40,41,43,44,45,46,47,55,56,57,61,73,79,82,99,100,101,102,103,104,107,108,],[-37,-41,-44,-47,-49,-51,-52,-54,-53,-38,-55,-50,-48,107,-56,-39,-40,-42,-43,-45,-46,-64,-61,]),'[':([21,51,56,],[52,52,52,]),'error':([60,63,],[84,87,]),'&':([60,63,],[85,88,]),'STRING':([68,],[94,]),'DIGIT_STRING':([68,],[97,]),'FLOAT_STRING':([68,],[98,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'function_list':([0,2,],[1,5,]),'function':([0,2,],[2,2,]),'empty':([0,2,18,24,126,136,137,],[3,3,25,25,25,25,25,]),'arguments':([7,11,15,],[9,16,19,]),'variable_or_pointer':([8,18,20,22,24,38,42,52,53,60,63,64,65,69,70,71,72,74,75,77,78,90,109,121,122,126,127,136,137,],[10,33,49,55,33,55,55,55,55,55,55,55,91,55,55,55,55,55,55,49,49,55,55,55,55,33,55,33,33,]),'body':([18,24,126,136,137,],[23,59,133,138,139,]),'line':([18,24,126,136,137,],[24,24,24,24,24,]),'declaration':([18,24,126,136,137,],[26,26,26,26,26,]),'assignment':([18,24,65,126,136,137,],[27,27,90,27,27,27,]),'if_clause':([18,24,126,136,137,],[28,28,28,28,28,]),'for_loop':([18,24,126,136,137,],[29,29,29,29,29,]),'expr_line':([18,24,126,136,137,],[30,30,30,30,30,]),'return_expr':([18,24,126,136,137,],[31,31,31,31,31,]),'printf_expr':([18,24,126,136,137,],[32,32,32,32,32,]),'expr_1':([18,22,24,38,52,53,60,63,64,69,70,90,109,121,122,126,127,136,137,],[34,54,34,66,79,81,83,86,89,99,100,117,81,131,132,34,134,34,34,]),'array':([18,20,22,24,38,42,52,53,60,63,64,65,69,70,71,72,74,75,77,78,90,109,121,122,126,127,136,137,],[35,50,57,35,57,57,57,57,57,57,57,92,57,57,57,57,57,57,50,50,57,57,57,57,35,57,35,35,]),'expr_2':([18,22,24,38,52,53,60,63,64,69,70,71,72,90,109,121,122,126,127,136,137,],[40,40,40,40,40,40,40,40,40,40,40,101,102,40,40,40,40,40,40,40,40,]),'expr_3':([18,22,24,38,52,53,60,63,64,69,70,71,72,74,75,90,109,121,122,126,127,136,137,],[41,41,41,41,41,41,41,41,41,41,41,41,41,103,104,41,41,41,41,41,41,41,41,]),'expr_4':([18,22,24,38,52,53,60,63,64,69,70,71,72,74,75,90,109,121,122,126,127,136,137,],[43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,43,]),'expr_5':([18,22,24,38,42,52,53,60,63,64,69,70,71,72,74,75,90,109,121,122,126,127,136,137,],[44,44,44,44,73,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,]),'expr_6':([18,22,24,38,42,52,53,60,63,64,69,70,71,72,74,75,90,109,121,122,126,127,136,137,],[45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,45,]),'function_call':([18,22,24,38,42,52,53,60,63,64,69,70,71,72,74,75,90,109,121,122,126,127,136,137,],[47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,47,]),'variable_list':([20,77,78,],[48,105,106,]),'arguments_call':([53,109,],[80,123,]),'digit':([68,],[95,]),'float':([68,],[96,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> function_list","S'",1,None,None,None),
  ('function_list -> function function_list','function_list',2,'p_function_list','mini_c.py',79),
  ('function_list -> empty','function_list',1,'p_function_list_empty','mini_c.py',83),
  ('function -> TYPE VARIABLE ( arguments ) { body }','function',8,'p_function_body','mini_c.py',99),
  ('arguments -> TYPE variable_or_pointer','arguments',2,'p_argunments_names_one','mini_c.py',109),
  ('arguments -> TYPE variable_or_pointer , arguments','arguments',4,'p_arguments_names_recursion','mini_c.py',113),
  ('arguments -> TYPE','arguments',1,'p_argunments_types_one','mini_c.py',117),
  ('arguments -> TYPE , arguments','arguments',3,'p_arguments_types_recursion','mini_c.py',121),
  ('body -> line body','body',2,'p_body_line_body','mini_c.py',130),
  ('body -> empty','body',1,'p_body_empty','mini_c.py',134),
  ('line -> declaration','line',1,'p_line_declaration','mini_c.py',149),
  ('line -> assignment','line',1,'p_line_assignment','mini_c.py',153),
  ('line -> if_clause','line',1,'p_line_if_clause','mini_c.py',157),
  ('line -> for_loop','line',1,'p_line_for_loop','mini_c.py',161),
  ('line -> expr_line','line',1,'p_line_expr','mini_c.py',165),
  ('line -> return_expr','line',1,'p_line_return','mini_c.py',169),
  ('line -> printf_expr','line',1,'p_line_printf','mini_c.py',173),
  ('declaration -> TYPE variable_list ;','declaration',3,'p_declaration','mini_c.py',180),
  ('declaration -> TYPE variable_list','declaration',2,'p_declaration_error_semicolon','mini_c.py',184),
  ('variable_list -> variable_or_pointer','variable_list',1,'p_variable_list_one','mini_c.py',189),
  ('variable_list -> array','variable_list',1,'p_variable_list_one','mini_c.py',190),
  ('variable_list -> variable_or_pointer , variable_list','variable_list',3,'p_variable_list_recursion','mini_c.py',196),
  ('variable_list -> array , variable_list','variable_list',3,'p_variable_list_recursion','mini_c.py',197),
  ('assignment -> variable_or_pointer = expr_1 ;','assignment',4,'p_assignment','mini_c.py',203),
  ('assignment -> array = expr_1 ;','assignment',4,'p_assignment','mini_c.py',204),
  ('assignment -> variable_or_pointer = error ;','assignment',4,'p_assignment_error_expr','mini_c.py',210),
  ('assignment -> array = error ;','assignment',4,'p_assignment_error_expr','mini_c.py',211),
  ('assignment -> variable_or_pointer = & VARIABLE ;','assignment',5,'p_assignment_address','mini_c.py',217),
  ('assignment -> array = & VARIABLE ;','assignment',5,'p_assignment_address','mini_c.py',218),
  ('return_expr -> RETURN expr_1 ;','return_expr',3,'p_return_expr','mini_c.py',223),
  ('return_expr -> RETURN ;','return_expr',2,'p_return_expr_empty','mini_c.py',227),
  ('expr_line -> expr_1 ;','expr_line',2,'p_expr_line','mini_c.py',231),
  ('printf_expr -> PRINTF ( STRING ) ;','printf_expr',5,'p_printf_expr_digit_float','mini_c.py',236),
  ('printf_expr -> PRINTF ( digit ) ;','printf_expr',5,'p_printf_expr_digit_float','mini_c.py',237),
  ('printf_expr -> PRINTF ( float ) ;','printf_expr',5,'p_printf_expr_digit_float','mini_c.py',238),
  ('digit -> DIGIT_STRING , expr_1','digit',3,'p_print_digit','mini_c.py',245),
  ('float -> FLOAT_STRING , expr_1','float',3,'p_print_float','mini_c.py',251),
  ('variable_or_pointer -> * VARIABLE','variable_or_pointer',2,'p_pointer','mini_c.py',259),
  ('variable_or_pointer -> VARIABLE','variable_or_pointer',1,'p_pointer','mini_c.py',260),
  ('expr_1 -> expr_2 > expr_1','expr_1',3,'p_expr_1_lr','mini_c.py',272),
  ('expr_1 -> expr_2 < expr_1','expr_1',3,'p_expr_1_lr','mini_c.py',273),
  ('expr_1 -> expr_2','expr_1',1,'p_expr_1_2','mini_c.py',283),
  ('expr_2 -> expr_3 PLUS expr_2','expr_2',3,'p_expr_2_lr','mini_c.py',289),
  ('expr_2 -> expr_3 - expr_2','expr_2',3,'p_expr_2_lr','mini_c.py',290),
  ('expr_2 -> expr_3','expr_2',1,'p_expr_2_3','mini_c.py',301),
  ('expr_3 -> expr_4 * expr_3','expr_3',3,'p_expr_3_lr','mini_c.py',307),
  ('expr_3 -> expr_4 / expr_3','expr_3',3,'p_expr_3_lr','mini_c.py',308),
  ('expr_3 -> expr_4','expr_3',1,'p_expr_3_4','mini_c.py',319),
  ('expr_4 -> - expr_5','expr_4',2,'p_expr_4','mini_c.py',325),
  ('expr_4 -> expr_5','expr_4',1,'p_expr_4','mini_c.py',326),
  ('expr_5 -> variable_or_pointer INCR','expr_5',2,'p_expr_5_incr','mini_c.py',339),
  ('expr_5 -> expr_6','expr_5',1,'p_expr_5_6','mini_c.py',349),
  ('expr_6 -> INTEGER','expr_6',1,'p_expr_6','mini_c.py',356),
  ('expr_6 -> variable_or_pointer','expr_6',1,'p_expr_6','mini_c.py',357),
  ('expr_6 -> function_call','expr_6',1,'p_expr_6','mini_c.py',358),
  ('expr_6 -> array','expr_6',1,'p_expr_6','mini_c.py',359),
  ('expr_6 -> ( expr_1 )','expr_6',3,'p_expr_6','mini_c.py',360),
  ('if_clause -> IF ( expr_1 ) { body }','if_clause',7,'p_if_only','mini_c.py',372),
  ('for_loop -> FOR ( assignment expr_1 ; expr_1 ) { body }','for_loop',10,'p_for_loop','mini_c.py',383),
  ('for_loop -> FOR ( assignment expr_1 ; expr_1 ) body }','for_loop',9,'p_for_loop_error_open_bracket','mini_c.py',394),
  ('for_loop -> FOR ( assignment expr_1 ; expr_1 ) { body','for_loop',9,'p_for_loop_error_close_bracket','mini_c.py',400),
  ('function_call -> VARIABLE ( arguments_call )','function_call',4,'p_function_call','mini_c.py',407),
  ('arguments_call -> expr_1','arguments_call',1,'p_arguments_names_call_one','mini_c.py',411),
  ('arguments_call -> expr_1 , arguments_call','arguments_call',3,'p_arguments_names_call_recursion','mini_c.py',415),
  ('array -> VARIABLE [ expr_1 ]','array',4,'p_array','mini_c.py',421),
  ('empty -> <empty>','empty',0,'p_empty','mini_c.py',427),
]
