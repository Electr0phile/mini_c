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
		cur_str = 'name: Name; args: ';
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
		print('SElf.var', self.var)
		self.expr = expr

	def __str__(self):
		return 'Assignment' + ' ' + str(self.var)

	def process(self):
		if self.var[1] not in symbol_table:
			not_declared_error(self.var[1])
		else:
			if self.var[0] == None:#regular case, not a pointer
				eval_res = evaluate(self.expr)
				memory_table[symbol_table[self.var[1]]] = eval_res
				print('{} assigned to {}'.format(self.var[1], eval_res))
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
		print(expr_dict);
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
		global rax, symbol_table, memory_table
		rax = evaluate(self.expr)
		print('Rax:', rax);
		symbol_table = symbol_table_stack.pop()
		prev_size = memory_table_stack.pop()
		memory_table = memory_table[:prev_size]
		#get_to_next_linenode();

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
		if cond_expr_val:
			global current_linenode
			symbol_table_stack.append(symbol_table.copy())
			history_table_stack.append(history_table.copy())
			self.visited = True
			current_linenode = self.body[0]
		else:
			get_to_next_linenode();


#looks up the symbol table or tells that there's no such variable
def lookup_value(expr):
	print("looking up:", expr, symbol_table)
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
		global current_linenode, symbol_table;
		if len(return_node_stack) == 0 or return_node_stack[-1] != current_linenode.next:
			return_node_stack.append(current_linenode.next);
		#print('SAVED TO RETURN STACK:', current_linenode.next);
		current_function = function_table[expr.name]
		current_linenode = current_function.start;
		symbol_table_stack.append(symbol_table.copy())
		history_table_stack.append(history_table.copy())
		memory_table_stack.append(len(memory_table));
		temp_symbol_table = {}
		i = 0;
		for argexpr in expr.arguments:
			#temp_symbol_table[current_function.arguments[i]['variable'][1]] = 
			eval_res = evaluate(argexpr)
			var = current_function.arguments[i]['variable']
			temp_symbol_table[var[1]] = len(memory_table);
			history_table[var[1]] = [eval_res]
			if var[0] == None:
				#symbol_table[var[1]] = len(memory_table);
				memory_table.append(eval_res);
			else:
				memory_table.append(Pointer(eval_res));
			i += 1;
		symbol_table = temp_symbol_table
		return get_user_input();


	if isinstance(expr, Expression):
		op = expr.op
		if op != None:
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
		print('expression inside if clause', expr)
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
		else:
			#print('Returning to:', return_node_stack[-1])
			current_linenode = return_node_stack.pop();
	if current_linenode == None:
		if len(return_node_stack) == 0:
			current_linenode = None
		else:
			current_linenode = return_node_stack.pop();		
	if current_linenode.next != None:
		current_linenode = current_linenode.next
		if isinstance(current_linenode.optype, IfClause):
			if current_linenode.optype.visited:
				current_linenode.optype.visited = False
				current_linenode = current_linenode.next
				global symbol_table
				symbol_table = symbol_table_stack.pop();
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
	print('Return node stack', return_node_stack);	
	user_inp = input().strip();
	user_cmd = user_inp.split();
	if len(user_cmd) == 0:
		return;
	if user_cmd[0] == 'print' or user_cmd[0] == 'p':
		if len(user_cmd) <= 1:
			print("Print command needs one parameter");
			return;
		else:
			print(lookup_value(user_cmd[1]))
	if user_cmd[0] == 'next' or user_cmd[0] == 'n':
		global next_cnt
		next_cnt = 1;
		if len(user_cmd) > 1:
			next_cnt = user_cmd[1];
		while (next_cnt):
			if (current_linenode.optype, ReturnStatement):
				return interpreter();
			else:
				interpreter();
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
	current_linenode.optype.process();
	if isReturn:
		return rax;
	
	

def start_interpreter():
	global current_linenode, symbol_table
	while current_linenode != None:
		get_user_input();
		if current_linenode == None and return_node_stack:
			current_linenode = return_node_stack.pop();
			if current_linenode == None:
				symbol_table = symbol_table_stack.pop()
		print(return_node_stack);
		#interpreter();
	print('Execution is complete');
	while (get_user_input()):
		pass;


init_interpreter();
#function_walk('main')
start_interpreter();
#function_walk('main');

		

	




