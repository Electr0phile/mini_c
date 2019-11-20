import json
import inspect
from mini_c import AST

function_table = {} # Str->Function
symbol_table = {} #Str -> Addr
history_table = {} #Str -> List[Val]
memory_table = {} #Int -> Val

addr_stack = [] #list of symbol_tables
rax = 0 #function return values stored here

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
		return ('Assignment' + ' ' + self.var + ' ' + str(self.expr));


class Expression:
	def __init__(self, op, left, right):
		if op == None:
			self.left = left;
		else:
			self.left = left;
			self.op = op;
			self.right = right;


class Declaration:
	def __init__(self, vartype, variables):
		self.vartype = vartype;
		self.variables = variables;
	def __str__(self):
		return 'Declaration:' + ' ' + self.vartype + ' ' + str(self.variables);

class IfClause:
	def __init__(self, expr, body):
		self.expr = expr;
		self.body = body;	

def init_function(function_map):
	name = function_map['function_name']
	args = function_map['arguments']
	line_node = get_flow_graph(function_map['body'])[0];
	#print(line_node);
	return Function(name, line_node, args);

def get_op(line_info):
	if line_info['type'] == 'assignment':
		var = line_info['value']['variable'] 
		expr = line_info['value']['expression']
		return Assignment(var, expr)
	if line_info['type'] == 'declaration':
		variables = line_info['value']['variables']
		vartype = line_info['value']['type'];
		return Declaration(vartype, variables);
	if line_info['type'] == 'if_clause':
		expr = line_info['value']['expr']
		body = get_flow_graph(line_info['value']['body']) # we have end and start of if clause here
		#print(body[0], body[1])
		return IfClause(expr, body);


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

def main():
	print("MAIN");
	startfunc = init_function(AST[1]);
	print(startfunc)
	start = startfunc.start;
	while (start != None):
		print('in cycle')
		print(start.lineno, start.optype);
		if isinstance(start.optype, IfClause):
			curnode = start.optype.body[0];
			while (curnode != None):
				print(curnode.lineno, curnode.optype);
				curnode = curnode.next
		start = start.next

main();


		

	




