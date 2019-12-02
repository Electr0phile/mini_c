import json
import inspect
from mini_c import AST

function_table = {} # Str->Function
symbol_table = {} #Str -> Addr
history_table = {} #Str -> List[Val] #saves history of a variable
memory_table = [] #Int -> Val 

symbol_table_stack = [] #stack of the symbol_tables, for implementing scopes;
addr_stack = [] #stack of nodes, used for implementing function call and return.
rax = 0 #function return values stored here
current_linenode = None

#Class Declarations
class Function:	
	def __init__(self, name, line_node, args):
		self.name = name
		self.start = line_node;
		self.args = args


class LineNode:
	def __init__(self, lineno, optype):
		self.lineno = lineno;
		self.optype = optype;
	def __str__ (self):
		return str(self.lineno) + ' ' + str(self.optype);


class Assignment:
	def __init__(self, var, expr):
		self.var = var
		self.expr = expr
	def __str__ (self):
		return ('Assignment' + ' ' + self.var)
	def process(self):
		if self.var in symbol_table == False:
			not_declared_error(self.var)
		else:
			memory_table[symbol_table[self.var]] = evaluate(self.expr)
			history_table[self.var].append(memory_table[symbol_table[self.var]])
		get_to_next_linenode();


class Expression:
	def __init__(self, op, left, right):
		if op == None:
			self.op = None;
			self.left = left;
			self.right = None;
		else:
			self.op = op;
			self.left = left;
			self.right = right;
	def __str__(self):
		return '\n' + str(self.op) + ' ' + str(self.left) + ' ' + str(self.right) + '\n';

#Makes expression out of a dictionary
def get_expression(expr_dict):
	if isinstance(expr_dict, str):
		return Expression(None, expr_dict, None);
	if isinstance(expr_dict, dict):
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
			symbol_table[var] = len(memory_table);
			memory_table.append('N/A');
			history_table[var] = ['N/A']
		get_to_next_linenode();



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
		if self.visited:
			print("it was visited")
			global symbol_table
			symbol_table = symbol_table_stack.pop();
			get_to_next_linenode();
			return;
		cond_expr_val = evaluate(self.expr);
		if cond_expr_val:
			global current_linenode
			symbol_table_stack.append(symbol_table.copy())
			self.visited = True
			current_linenode = self.body[0]
		else:
			get_to_next_linenode();


#looks up the symbol table or tells that there's no such variable
def lookup_value(expr):
	print("Looking up " + expr);
	print(symbol_table);
	print(expr in symbol_table);
	if expr in symbol_table:
		return memory_table[symbol_table[expr]]
	else:
		not_declared_error(expr);


#function for showing errors about undefined variables
def not_declared_error(var):
	print("Variable {} is not declared".format(var))


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
	if isinstance(expr, str):
		if expr.isdigit():
			return int(expr)
		if is_float(expr):
			return float(expr)
		else:
			return lookup_value(expr);
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
		variables = line_info['value']['variables']
		vartype = line_info['value']['type'];
		return Declaration(vartype, variables);
	if line_info['type'] == 'if_clause':
		expr = line_info['value']['expr']
		body = get_flow_graph(line_info['value']['body']) # we have end and start of if clause here
		#print("If body start and end", end = ': ')
		#print(body[0], body[1])
		return IfClause(get_expression(expr), body);


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

def get_to_next_linenode():
	global current_linenode
	if current_linenode == None:
		if len(addr_stack) == 0:
			current_linenode = None
		else:
			current_linenode = addr_stack.pop();		
	if current_linenode.next != None:
		current_linenode = current_linenode.next
		if isinstance(current_linenode.optype, IfClause):
			if current_linenode.optype.visited:
				current_linenode = current_linenode.next
				global symbol_table
				symbol_table = symbol_table_stack.pop();
	else:
		if len(addr_stack) == 0:
			current_linenode = None
		else:
			current_linenode = addr_stack.pop();



def start_interpreter():
	while current_linenode != None:
		user_inp = input().strip();
		user_cmd = user_inp.split();
		print(current_linenode);
		print('Symbol table', symbol_table);
		print('Symbol table stack', symbol_table_stack);
		print('Memory table', memory_table);
		print('History table', history_table);
		print(user_cmd);
		if len(user_cmd) == 0:
			continue;
		if user_cmd[0] == 'next' or user_cmd[0] == 'n':
			next_cnt = 1;
			if len(user_cmd) > 1:
				next_cnt = user_cmd[1];
			while (next_cnt):
				current_linenode.optype.process();
				# get_to_next_linenode();
				next_cnt -= 1
		if user_cmd[0] == 'print' or user_cmd[0] == 'p':
			if len(user_cmd) <= 1:
				print("Print command needs one parameter");
				continue
			else:
				print(lookup_value(user_cmd[1]))		
	print('Execution is complete');
	user_inp = ''
	while (user_inp != 'q'):
		user_inp = input().strip();
		user_cmd = user_inp.split();
		print(current_linenode);
		print('Symbol table', symbol_table);
		print('Symbol table stack', symbol_table_stack);
		print('Memory table', memory_table);
		print('History table', history_table);
		print(user_cmd);
		if len(user_cmd) == 0:
			continue;
		if user_cmd[0] == 'print' or user_cmd[0] == 'p':
			if len(user_cmd) <= 1:
				print("Print command needs one parameter");
				continue
			else:
				print(lookup_value(user_cmd[1]))				




init_interpreter();
#function_walk('main')
start_interpreter();
#function_walk('main');

		

	




