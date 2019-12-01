import json
import inspect
from mini_c import AST

function_table = {} # Str->Function
symbol_table = {} #Str -> Addr
history_table = {} #Str -> List[Val] #saves history of a variable
memory_table = [] #Int -> Val 

env_stack = [] #stack of the symbol_tables, for implementing scopes;
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
		return ('Assignment' + ' ' + self.var + ' ' + str(evaluate(self.expr)))
	def process(self):
		if self.var in symbol_table == False:
			not_declared_error(self.var)
		else:
			memory_table[symbol_table[self.var]] = evaluate(self.expr)


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
		for var in variables:
			symbol_table[var] = len(memory_table);
			memory_table.append(0);


class IfClause:
	def __init__(self, expr, body):
		self.expr = expr;
		self.body = body;
	def __str__(self):
		cur_str = ''
		start = self.body[0];
		while start != None:
			cur_str += str(start) + ' '
			start = start.next
		return cur_str;

#looks up the symbol table or tells that there's no such variable
def lookup_value(expr):
	if expr in symbol_table:
		return memory_table[symbol_table[expr]]
	else:
		not_declared_error(expr);


#function for showing errors about undefined variables
def not_declared_error(var):
	printf("Variable {} is not declared".format(var))


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
		op = ex pr.op
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
		if op == None:
			return evaluate(expr.left);			


def init_function(function_map):
	name = function_map['function_name']
	print(name);
	args = function_map['arguments']
	line_node = get_flow_graph(function_map['body'])[0];
	#print(line_node);
	return Function(name, line_node, args);


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
		expr = line_info['value']['expression']
		body = get_flow_graph(line_info['value']['body']) # we have end and start of if clause here
		#print(body[0], body[1])
		return IfClause(get_expression(expr), body);


def get_flow_graph(body):
	line_prev = None
	line_start = None;
	for line_info in body:
		lineno = line_info['span'][0];
		optype = get_op(line_info);
		cur_line_node = LineNode(lineno, optype);
		cur_line_node.next = None;
		if line_prev != None:
			line_prev.next = cur_line_node;
			if isinstance(line_prev.optype, IfClause):
				line_prev.optype.body[1].next = cur_line_node;
		if line_start == None:
			line_start = cur_line_node
		#print(cur_line_node);
		line_prev = cur_line_node;
	return (line_start, line_prev);


def main(index): 
	startfunc = init_function(AST[index]);
	print(startfunc)
	start = startfunc.start;
	while (start != None):
		print('in cycle')
		print(start.lineno, type(start.optype), start.optype);
		start = start.next

main(0);
main(1);


		

	




