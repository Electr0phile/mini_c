import json
import inspect
from mini_c import AST

function_table = {} # Str->Function
symbol_table = {} #Str -> Addr
history_table = {} #Str -> List[Val] #saves history of a variable
memory_table = [] #Int -> Val 
next_cnt = 0; #parameter of the next line function
symbol_table_stack = [] #stack of the symbol_tables, for implementing scopes;
history_table_stack = [] #stack of the history tables, used for showing right history, according to the scope
return_node_stack = [] #stack of nodes, used for implementing function call and return.
memory_table_stack = [] #will store the size of memory_table before function calls, so that we clear unnecessary memory after a function call 
scope_stack = [] 		#needed for implementing scopes, it basically stores which function was called
rax = 0 #function return values stored here
current_linenode = None


# Class Declarations
class Function:	
	def __init__(self, name, line_node, arguments):
		self.name = name
		self.start = line_node;
		self.arguments = arguments

class FunctionCall:
	def __init__(self, name, arguments):
		self.name = name
		self.arguments = arguments
	def __str__(self):
		cur_str = 'name: {}; args: '.format(self.name);
		for arg in self.arguments:
			cur_str += str(arg) +' '
		return cur_str

		


class LineNode:
	def __init__(self, lineno, optype):
		self.lineno = lineno;
		self.optype = optype;

	def __str__(self):
		return str(self.lineno) + ' ' + str(self.optype);


class Assignment:
	def __init__(self, var, expr):
		self.var = var
		self.expr = expr

	def __str__(self):
		return 'Assignment' + ' ' + str(self.var)

	def process(self):
		global current_linenode
		assignment_linenode = current_linenode;
		if self.var[1] not in symbol_table:
			not_declared_error(self.var[1])
		else:
			if self.var[0] == None:#regular case, not a pointer
				eval_res = evaluate(self.expr)
				print("assigning to {}, eval_res = {}".format(self.var[1], eval_res))
				#if type(eval_res) == type(lookup_value)
				memory_table[symbol_table[self.var[1]]] = eval_res
				print('before error', history_table)
				print(history_table_stack)
				print(symbol_table)
				print(memory_table)
				history_table[self.var[1]].append(memory_table[symbol_table[self.var[1]]])
			else:#pointer case with a star in front of it
				eval_res = evaluate(self.expr)
				pointer_val = memory_table[symbol_table[self.var[1]]]	
				if isinstance(pointer_val, Pointer) and pointer_val.addr != None and pointer_val.addr < len(memory_table): 
					memory_table[pointer_val.addr] = eval_res
				else:
					if isinstance(pointer_val, Pointer):
						invalid_pointer_error(pointer_val)
					else:
						not_a_pointer_error(pointer_val)
		current_linenode = assignment_linenode
		get_to_next_linenode()


class Expression:
	def __init__(self, op, left, right):
		self.op = op;
		self.left = left;
		self.right = right;

	def __str__(self):
		return 'Expression:' + str(self.op) + ' ' + str(self.left) + ' ' + str(self.right) + '\n';


# Makes expression out of a dictionary
def get_expression(expr_dict):
	if isinstance(expr_dict, str):
		return Expression(None, expr_dict, None);
	if isinstance(expr_dict, tuple):
		return Expression(None, expr_dict, None)
	if isinstance(expr_dict, dict):
		if 'function_name' in expr_dict:
			function_name = expr_dict['function_name']
			arguments_dict = expr_dict['arguments']
			arguments = [get_expression(arg['expression']) for arg in arguments_dict]
			left = FunctionCall(function_name, arguments);
			return Expression(None, left, None);
		left = expr_dict['left']
		right = expr_dict['right']
		op = expr_dict['op']
		return Expression(op, get_expression(left), get_expression(right)); 


class Declaration:
	def __init__(self, vartype, variables):
		self.vartype = vartype;
		self.variables = variables;
	def __str__(self):
		return 'Declaration:' + ' ' + self.vartype + ' ' + str(self.variables);
	def process(self):
		for var in self.variables:
			#var = [null, name]
			symbol_table[var[1]] = len(memory_table);
			history_table[var[1]] = ['N/A']
			if var[0] == None:
				#symbol_table[var[1]] = len(memory_table);
				memory_table.append('N/A');
			else:
				memory_table.append(Pointer(None));
		get_to_next_linenode();

class ReturnStatement:
	def __init__(self, expr):
		self.expr = expr;
	def process(self):
		global rax, symbol_table, memory_table, history_table
		rax = evaluate(self.expr)
		print('Rax:', rax);
		print('Scope stack before:', scope_stack);
		while scope_stack[-1] == 1:
			symbol_table_stack.pop()
			#revert_history_table();
			history_table_stack.pop()
			scope_stack.pop();
		symbol_table = symbol_table_stack.pop()
		history_table = history_table_stack.pop()
		#revert_history_table();
		scope_stack.pop();
		print('Scope stack after:', scope_stack);
		prev_size = memory_table_stack.pop()
		memory_table = memory_table[:prev_size]
		print(symbol_table);
		print(memory_table)
		print('changed to', history_table);
		print(symbol_table_stack)
		print(history_table_stack);
		get_to_next_linenode(True);

class Pointer:
	def __init__(self, addr):
		self.addr = addr
	def __str__(self):
		return 'Pointer with addr: ' + str(self.addr)

class IfClause:
	def __init__(self, expr, body):
		self.expr = expr;
		self.body = body;
		self.visited = False

	def __str__(self):
		cur_str = 'IF CLAUSE'
		#start = self.body[0];
		#while start != None:
		#	cur_str += str(start) + ' '
		#	start = start.next
		return cur_str;
	def process(self):
		cond_expr_val = evaluate(self.expr);
		print("condition is:", cond_expr_val)
		if cond_expr_val:
			print('condition is true')
			global current_linenode
			symbol_table_stack.append(symbol_table.copy())
			history_table_stack.append(history_table.copy())
			self.visited = True
			scope_stack.append(1)
			current_linenode = self.body[0]
		else:
			print("Condition is false, so we are going to the next line")
			get_to_next_linenode();
			print(current_linenode);


#looks up the symbol table or tells that there's no such variable
def lookup_value(expr):
	#print("looking up:", expr, symbol_table)
	if expr in symbol_table:
		return memory_table[symbol_table[expr]]
	else:
		not_declared_error(expr);

#dereference pointer
def deref_pointer(pointer):
	if isinstance(pointer, Pointer) and pointer.addr != None and pointer.addr < len(memory_table): 
		return memory_table[pointer.addr]
	else:
		if isinstance(pointer, Pointer):
			invalid_pointer_error(pointer.addr)
		else:
			not_a_pointer_error(pointer)


#get addr of a variable
def get_var_address(var):
	if var in symbol_table:
		return symbol_table[var]
	else:
 		not_declared_error(var)

#function for showing errors about undefined variables
def not_declared_error(var):
	print("Variable {} is not declared".format(var))

def invalid_pointer_error(addr):
	print("Access to invalid address: {}".format(addr)) 

def not_a_pointer_error(var):
	print("The variable {} is not a pointer".format(var))

def revert_history_table():
	print("WE ARE REVERTING")
	global history_table, history_table_stack
	last_history_table = history_table_stack.pop()
	print('Reverting:\n', history_table, '\n', last_history_table)
	for var in last_history_table:
		if var in history_table and is_prefix(last_history_table[var], history_table[var]):
			last_history_table[var] = history_table[var]
	history_table = last_history_table;
	print('changed to', history_table)

def is_prefix(list_a, list_b):
	if len(list_b) < len(list_a):
		return False
	for i in range(len(list_a)):
		if list_a[i] != list_b[i]:
			return False
	return True			

def is_float(expr):
	try:
		float(expr)
		return True;
	except ValueError:
		return False


def is_string(expr):
	return type(expr) == type('')


#Evaluates expression to some value
def evaluate(expr):
	#print("evaluating", expr)
	if isinstance(expr, str):
		if expr.isdigit():
			return int(expr)
		if is_float(expr):
			return float(expr)
	if isinstance(expr, tuple):
		if expr[0] == None:
			return lookup_value(expr[1])
		elif expr[0] == '*':
			return deref_pointer(lookup_value(expr[1]));
		elif expr[0] == '&':
			return Pointer(get_var_address(expr[1]))
	if isinstance(expr, FunctionCall):
		global current_linenode, symbol_table, history_table
		if current_linenode != None:
			return_node_stack.append(current_linenode.next);
			print('SAVED TO RETURN STACK:', current_linenode.next);
		scope_stack.append(expr.name)
		current_function = function_table[expr.name]
		print('First line of the function', expr.name, current_linenode);
		symbol_table_stack.append(symbol_table.copy())
		history_table_stack.append(history_table.copy())
		memory_table_stack.append(len(memory_table));
		temp_symbol_table = {}
		temp_history_table = {}
		i = 0;
		for argexpr in expr.arguments:
			#temp_symbol_table[current_function.arguments[i]['variable'][1]] = 
			eval_res = evaluate(argexpr)
			var = current_function.arguments[i]['variable']
			temp_symbol_table[var[1]] = len(memory_table);
			temp_history_table[var[1]] = [eval_res]
			if var[0] == None:
				#symbol_table[var[1]] = len(memory_table);
				memory_table.append(eval_res);
			else:
				if not isinstance(eval_res, Pointer):
					memory_table.append(Pointer(eval_res));
				else:
					memory_table.append(eval_res);
			i += 1;
		symbol_table = temp_symbol_table
		history_table = temp_history_table
		print('entering a function with', history_table)
		current_linenode = current_function.start;
		return get_user_input();


	if isinstance(expr, Expression):
		op = expr.op
		if op != None:
			#print('Evaluation with operation:', op);
			if op == '+':
				return evaluate(expr.left) + evaluate(expr.right);
			if op == '-':
				return evaluate(expr.left) - evaluate(expr.right);
			if op == '*':
				return evaluate(expr.left) * evaluate(expr.right);
			if op == '/':
				divisor = evaluate(expr.right)
				if divisor == 0 :
					raise ZeroDivisionError;
				return evaluate(expr.left) / divisor;
			if op == '>':
				return evaluate(expr.left) > evaluate(expr.right)
			if op == '<':
				return evaluate(expr.left) < evaluate(expr.right)
			if op == '==':
				return evaluate(expr.left) == evaluate(expr.right)
		if op == None:
			return evaluate(expr.left);			


def init_function(function_dict):
	name = function_dict['function_name']
	args = function_dict['arguments']
	line_node = get_flow_graph(function_dict['body'])[0];
	#print(line_node);
	cur_function = Function(name, line_node, args);
	function_table[name] = cur_function
	return cur_function


def get_op(line_info):
	if line_info['type'] == 'assignment':
		var = line_info['value']['variable'] 
		expr = line_info['value']['expression']
		return Assignment(var, get_expression(expr))
	if line_info['type'] == 'declaration':
		is_pointer = line_info['value']['variables'][0] == '*' 		
		variables = line_info['value']['variables']
		vartype = line_info['value']['type'];
		return Declaration(vartype, variables);
	if line_info['type'] == 'if_clause':
		expr = line_info['value']['expression']
		#print('expression inside if clause', expr)
		body = get_flow_graph(line_info['value']['body']) # we have end and start of if clause here
		#print("If body start and end", end = ': ')
		#print(body[0], body[1])
		return IfClause(get_expression(expr), body);
	if line_info['type'] == 'return':
		expr = line_info['value']['expression']
		return ReturnStatement(get_expression(expr))


def get_flow_graph(body):
	line_prev = None 
	line_start = None;
	for line_info in body:
		lineno = line_info['span'][0];
		optype = get_op(line_info);
		cur_line_node = LineNode(lineno, optype);
		#print(cur_line_node)
		if isinstance(cur_line_node.optype, IfClause):
			#print('prev_line: ' + str(cur_line_node))
			cur_line_node.optype.body[1].next = cur_line_node;
		cur_line_node.next = None;
		print(cur_line_node);
		if line_prev != None:
			print('prev_line' + str(line_prev))
			line_prev.next = cur_line_node;
		if line_start == None:
			line_start = cur_line_node
		#print(cur_line_node);
		line_prev = cur_line_node;
	return (line_start, line_prev);


def function_walk(name): 
	startfunc = function_table[name] 
	print(startfunc)
	start = startfunc.start;
	while (start != None):
		print('in cycle')
		print(start.lineno, type(start.optype), start.optype);
		start = start.next

def init_interpreter():
	for i in range(len(AST)):
		init_function(AST[i]);
	global current_linenode;
	current_linenode = function_table['main'].start;

def get_to_next_linenode(isReturn = False):
	global current_linenode
	if isReturn:
		if len(return_node_stack) == 0:
			current_linenode = None
			return
		else:
			print('Returning to:', return_node_stack[-1])
			current_linenode = return_node_stack.pop();
			return
		return
	if current_linenode == None:
		if len(return_node_stack) == 0:
			current_linenode = None
			return
		else:
			current_linenode = return_node_stack.pop();		
			return
	if current_linenode.next != None:
		#print(current_linenode)
		current_linenode = current_linenode.next
		if isinstance(current_linenode.optype, IfClause):
			if current_linenode.optype.visited:
				print(current_linenode)
				current_linenode.optype.visited = False
				scope_stack.pop();
				current_linenode = current_linenode.next
				global symbol_table
				symbol_table = symbol_table_stack.pop();
				revert_history_table();
				return
	else:
		if len(return_node_stack) == 0:
			current_linenode = None
		else:
			#print('Returning to:', return_node_stack[-1])
			current_linenode = return_node_stack.pop();



def get_user_input():
	print(current_linenode);
	print('Symbol table', symbol_table);
	print('Symbol table stack', symbol_table_stack);
	print('Memory table', memory_table);
	print('History table', history_table);
	print('History table stack', history_table_stack);
	print('Return node stack', return_node_stack);	
	global next_cnt;
	while next_cnt:
		print('we are here with + next cnt')
		if (current_linenode == None):
			return;
		while not isinstance(current_linenode.optype, ReturnStatement):
			interpreter();
			#print('symbol_table', symbol_table)
			return get_user_input();
		if isinstance(current_linenode.optype, ReturnStatement):
			#print('IT IS A RETURN STATEMENT', current_linenode);
			return interpreter();

	user_inp = input().strip();
	user_cmd = user_inp.split();
	if len(user_cmd) == 0:
		return;
	if user_cmd[0] == 'print' or user_cmd[0] == 'p':
		while (user_cmd[0] == 'print' or user_cmd[0] == 'p'):
			if len(user_cmd) <= 1:
				print("Print command needs one parameter");
			else:
				print(lookup_value(user_cmd[1]))
			user_inp = input().strip();
			user_cmd = user_inp.split();
	if user_cmd[0] == 'next' or user_cmd[0] == 'n':
		#global next_cnt
		next_cnt = 1;
		if len(user_cmd) > 1:
			next_cnt = int(user_cmd[1]);
		while (next_cnt):
			print('we are here')
			if (current_linenode == None):
				return;
			while not isinstance(current_linenode.optype, ReturnStatement):
				interpreter();
				#print('symbol_table', symbol_table)
				return get_user_input();
			if isinstance(current_linenode.optype, ReturnStatement):
				#print('IT IS A RETURN STATEMENT', current_linenode);
				return interpreter();
			#else:
			#	interpreter();
			#current_linenode.optype.process();
			# get_to_next_linenode();
			

def interpreter():
	global next_cnt
	if next_cnt == 0:
		return
	next_cnt -= 1;
	isReturn = False;
	if isinstance(current_linenode.optype, ReturnStatement):
		isReturn = True
	#print(isReturn)
	#print(current_linenode);
	current_linenode.optype.process();
	#print('Return_node_stack:', return_node_stack);
	if isReturn:
		return rax;
	
	

def start_interpreter():
	global current_linenode, symbol_table
	while current_linenode != None:
		get_user_input();
		
	print('Execution is complete');
	while (get_user_input()):
		pass;


init_interpreter();
#function_walk('main')
start_interpreter();
#function_walk('main');

		

	




