import json
import inspect
from minicparser import parse
#import sys
#sys.setrecursionlimit(10000)

AST, ERRORS, code_lines = parse()

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
no_of_invalid_commands = 0
current_linenode = None
show_line_info = ''


available_commands = "\
   ************************************************************\n\
	Commands       Parameter           Description\n\
	print | p         v           prints the current value of v\n\
	trace | t         v           prints the value history of v\n\
	next  | n        -|n          executes the current line or next n lines \n\
	help  | h         -           prints this message\n\
	quit  | q         -           exits the debugger\n"

def run_time_error(str):
	print ("Error!!!! ", str)
	exit();

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
		if isinstance(self.var, tuple): # not arrays
			# print('Assigning to', self.var[1], end = ': ');
			if self.var[1] not in symbol_table:
				not_declared_error(self.var[1])
				run_time_error('Assignment to undeclared variable\n');
			else:
				if self.var[0] == None:#regular case, not a pointer
					eval_res = evaluate(self.expr)
					eval_res = typecast(history_table[self.var[1]][0][2], eval_res);
					# print(eval_res)
					memory_table[symbol_table[self.var[1]]] = eval_res
					history_table[self.var[1]].append((eval_res, assignment_linenode.lineno))
				else:#pointer case with a star in front of it
					eval_res = evaluate(self.expr)
					#pointer_val = memory_table[symbol_table[self.var[1]]]
					pointer_val = lookup_value(self.var[1])	
					if isinstance(pointer_val, Array):
						pointer_val = Pointer(pointer_val.startAddress)
					if isinstance(pointer_val, Pointer) and pointer_val.addr != None and pointer_val.addr < len(memory_table): 
						memory_table[pointer_val.addr] = eval_res
						if hasattr(pointer_val, 'varname'):
							# print(pointer_val.varname, pointer_val.scope);
							if pointer_val.scope == len(symbol_table_stack):
								history_table[pointer_val.varname].append((eval_res, assignment_linenode.lineno));
							else:
								(history_table_stack[pointer_val.scope][pointer_val.varname]).append((eval_res, assignment_linenode.lineno));
					else:
						if isinstance(pointer_val, Pointer):
							invalid_pointer_error(pointer_val)
						else:
							not_a_pointer_error(self.var[1])
		if isinstance(self.var, dict): # when it is an array
			array = lookup_value(self.var['array_name'])
			#array = symbol_table[self.var['array_name']]
			index = evaluate(get_expression(self.var['index']))
			if (index >= 0 and index < array.length and int(index) == index):
				eval_res = typecast(array.arrayType, evaluate(self.expr));
				memory_table[array.startAddress + int(index)] = eval_res
			else:
				run_time_error("Illegal array index, index = " + str(index) + ", the size is " + str(array.length))

		current_linenode = assignment_linenode
		# print("Calling get_to_next_linenode from assignment")
		get_to_next_linenode()

class PrintfStatement:
	def __init__(self, printf_type, val):
		self.printf_type = printf_type
		self.val = val;
	def process(self):
		cur_str = ''
		#print(self.val);
		# print(self.printf_type);
		if self.printf_type == 'str':
			i = 1;
			while i < len(self.val) - 1:
				if self.val[i] == '\\' and self.val[i+1] == 'n':
					cur_str += '\n'
					i += 1
				else:
					cur_str += self.val[i]
				i += 1
			print(cur_str, end = '')
		else:
			eval_res = evaluate(self.val)
			if self.printf_type == 'int':
				print(int(eval_res))
			else:
				print(float(eval_res))
		get_to_next_linenode()

class ExpressionLine:
	def __init__(self, expr):
		self.expr = expr;
	def process(self):
		global current_linenode;
		expr_linenode = current_linenode
		evaluate(self.expr);
		current_linenode = expr_linenode
		get_to_next_linenode();




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

		if 'variable' in expr_dict: # the for loop initialization expression
			return Assignment(expr_dict['variable'], expr_dict['expression'])

		elif 'function_name' in expr_dict:
			function_name = expr_dict['function_name']
			arguments_dict = expr_dict['arguments']
			arguments = [get_expression(arg['expression']) for arg in arguments_dict]
			left = FunctionCall(function_name, arguments);
			return Expression(None, left, None);
		elif 'array_name' in expr_dict:
			return expr_dict;

		else :
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
		global current_linenode;
		declaration_linenode = current_linenode
		for var in self.variables:
			if isinstance(var, dict): # when it is an array 
				arr_name = var['array_name']
				arr_size = evaluate(get_expression(var['index']))
				if (int(arr_size) == arr_size):
					symbol_table[arr_name] = Array(self.vartype, len(memory_table), arr_size)
					for i in range(arr_size):
						memory_table.append('0')
				else:
					run_time_error("Array index should be an integer but given " + str(arr_size))

			#var = [null, name]
			else:
				symbol_table[var[1]] = len(memory_table);
				history_table[var[1]] = [('N/A', current_linenode.lineno, self.vartype)]
				if var[0] == None:
					#symbol_table[var[1]] = len(memory_table);
					memory_table.append('N/A');
				else:
					memory_table.append(Pointer('N/A'));
		current_linenode = declaration_linenode
		get_to_next_linenode();

class ReturnStatement:
	def __init__(self, expr):
		self.expr = expr;
	def process(self):
		global rax, symbol_table, memory_table, history_table
		rax = evaluate(self.expr)
		# print('Rax:', rax);
		#print('Scope stack before:', scope_stack);
		while len(scope_stack) and scope_stack[-1] == 1:
			symbol_table_stack.pop()
			#revert_history_table();
			history_table_stack.pop()
			scope_stack.pop();
		if len(symbol_table_stack):
			symbol_table = symbol_table_stack.pop()
			history_table = history_table_stack.pop()
			#revert_history_table();
			scope_stack.pop();
			#print('Scope stack after:', scope_stack);
			prev_size = memory_table_stack.pop()
			memory_table = memory_table[:prev_size]
			#print(symbol_table);
			#print(memory_table)
			#print('changed to', history_table);
			#print(symbol_table_stack)
			#print(history_table_stack);
		get_to_next_linenode(True);

class Pointer:
	def __init__(self, addr):
		self.addr = addr
		# self.varname = varname;
		# self.scope_index = index;
	def __str__(self):
		return 'Pointer with addr: ' + str(self.addr)

class Array:
	def __init__(self, arrayType, startAddress, length):
		self.arrayType = arrayType
		self.startAddress = startAddress
		self.length = length
	def __str__(self):
		return 'Array of type ' + self.arrayType + " starting at " +  str(self.startAddress) + ' with length ' + str(self.length)


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
		global current_linenode
		main_if_node = current_linenode
		cond_expr_val = evaluate(self.expr);
		#print("condition is:", cond_expr_val)
		if cond_expr_val:
			#print('condition is true')
			symbol_table_stack.append(symbol_table.copy())
			history_table_stack.append(history_table.copy())
			self.visited = True
			scope_stack.append(1)
			current_linenode = self.body[0]
		else:
			#print("Condition is false, so we are going to the next line")
			current_linenode = main_if_node # Restore the main node
			get_to_next_linenode();
			#print(current_linenode);


class ForLoop:
	def __init__(self, initialization, condition, update, body):
		self.initialization = initialization
		self.condition = condition
		self.update = update
		self.body = body
		self.firstEntry = True
		self.visited = False

	def __str__(self):
		return "ForLoop"

	def process(self):
		global current_linenode, symbol_table
		for_loop_linenode = current_linenode;
		#if not self.visited:
		if self.firstEntry:
			#print("the for loop initialization is ", self.initialization)
			self.initialization.process()
			self.firstEntry = False
			#self.visited = True
		else:
			#print('evaluation of increment', self.update)
			evaluate(self.update)

		satisfied = evaluate(self.condition)
		if satisfied:
			#print("**********************condition satisfied******************")
			#if self.visited
			if not self.visited:
				symbol_table_stack.append(symbol_table.copy())
				history_table_stack.append(history_table.copy())
				self.visited = True
				scope_stack.append(1)
			current_linenode = self.body[0];
		else:
			current_linenode = for_loop_linenode;
			self.firstEntry = True
			if self.visited:
				self.visited = False
				self.firstEntry = True
				scope_stack.pop()
				symbol_table = symbol_table_stack.pop()
				revert_history_table();	
			get_to_next_linenode()


#looks up the symbol table or tells that there's no such variable
def lookup_value(var):
	#print("looking up:", expr, symbol_table)
	if var in symbol_table:
		if isinstance(symbol_table[var], Array):
			return symbol_table[var]
		return memory_table[symbol_table[var]]
	else:
		return not_declared_error(var);

def trace(var):
	if var in history_table:
		ans = ''
		for values in history_table[var]:
			ans += (var + ' = ' + str(values[0]) + ' at line ' + str(values[1]) +'\n');
		return ans
	else:
		return not_declared_error(var) + '\n';

#dereference pointer
def deref_pointer(pointer, var):
	if isinstance(pointer, Array):
		pointer = Pointer(pointer.startAddress)
	if isinstance(pointer, Pointer) and pointer.addr != None and pointer.addr < len(memory_table): 
		return memory_table[pointer.addr]
	else:
		if isinstance(pointer, Pointer):
			invalid_pointer_error(pointer.addr)
		else:
			not_a_pointer_error(var)


#get addr of a variable
def get_var_address(var):
	if var in symbol_table:
		if isinstance(symbol_table[var], Array):
			return (symbol_table[var]).startAddress
		return symbol_table[var]
	else:
 		#not_declared_error(var)
 		run_time_error('& operand used to an undeclared variable "' + var + '"')

#function for showing errors about undefined variables
def not_declared_error(var):
	return ('Variable "{}" is not declared'.format(var))

def invalid_pointer_error(addr):
	print("Access to invalid address: {}".format(addr)) 
	run_time_error('');

def not_a_pointer_error(var):
	print('The variable "{}" is not a pointer'.format(var))
	run_time_error('');

def revert_history_table():
	#print("WE ARE REVERTING")
	global history_table, history_table_stack
	last_history_table = history_table_stack.pop()
	#print('Reverting:\n', history_table, '\n', last_history_table)
	for var in last_history_table:
		if var in history_table and is_prefix(last_history_table[var], history_table[var]):
			last_history_table[var] = history_table[var]
	history_table = last_history_table;
	#print('changed to', history_table)

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

def typecast(vartype, val):
	# print("casting format ", str(vartype), " to ", str(val))
	if isinstance(val, Pointer):
		return val;
	if vartype == 'int':
		return int(val)
	if vartype == 'float':
		return float(val)
	else:
		return "error"



#Evaluates expression to some value
def evaluate(expr):
	global current_linenode, symbol_table, history_table
	
	if isinstance(expr, str): # immediate value
		if expr.isdigit():
			return int(expr)
		if is_float(expr):
			return float(expr)
	
	if isinstance(expr, tuple): # Not arrays, just a variable name
		if expr[0] == None:# Not a pointer case
			if expr[1] in symbol_table:
				return lookup_value(expr[1])
			else:
				run_time_error('Undeclared reference to ' + expr[1])
		elif expr[0] == '*':#Dereferencing a pointer
			return deref_pointer(lookup_value(expr[1]), expr[1]);
		elif expr[0] == '&':#Obtaining address of a variable
			cur_pointer = Pointer(get_var_address(expr[1]));
			cur_pointer.varname = expr[1];
			cur_pointer.scope = len(symbol_table_stack)
			# return Pointer(get_var_address(expr[1]))
			return cur_pointer
	
	if isinstance(expr, dict): # array indexing
		array = symbol_table[expr['array_name']]
		if isinstance(array, int):
			array = memory_table[array]
		index = evaluate(get_expression(expr['index']))
		mxsize = 0;
		addr = 0;
		# print(array);
		if isinstance(array, Array):
			# print('it was an array')
			addr = array.startAddress + int(index)
			mxsize = array.startAddress + array.length
		if isinstance(array, Pointer):
			# print('it is a pointer')
			addr = array.addr + index
			mxsize = len(memory_table)

		if (int(index) == index and 0 <= addr < mxsize):
			return memory_table[addr]
		else:
			# print(mxsize, index);
			run_time_error("Illegal array index, index = " + str(index))
	
	if isinstance(expr, FunctionCall):
		if current_linenode != None:
			return_node_stack.append(current_linenode.next);
			# print('SAVED TO RETURN STACK:', current_linenode.next);
		scope_stack.append(expr.name)
		current_function = None;
		if expr.name in function_table:
			current_function = function_table[expr.name]
		else:
			run_time_error("Undeclared reference to function " + '"' + expr.name + '"')
		#print('First line of the function', expr.name, current_linenode);
		symbol_table_stack.append(symbol_table.copy())
		history_table_stack.append(history_table.copy())
		memory_table_stack.append(len(memory_table));
		temp_symbol_table = {}
		temp_history_table = {}
		i = 0;

		if (len(expr.arguments) != len(current_function.arguments)):
			run_time_error("Incorrect number of arguments for function " + current_function.name + " expected " + str(len(current_function.arguments)) + " but got " + str(len(expr.arguments)))

		for argexpr in expr.arguments:
			#temp_symbol_table[current_function.arguments[i]['variable'][1]] = 
			eval_res = evaluate(argexpr)
			if isinstance(eval_res, Array):
				eval_res = eval_res.startAddress
			var = current_function.arguments[i]['variable'] 
			vartype = current_function.arguments[i]['type']
			temp_symbol_table[var[1]] = len(memory_table);
			eval_res = typecast(vartype, eval_res)
			temp_history_table[var[1]] = [(eval_res, current_function.start.lineno, vartype)]
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
		#print('entering a function with', history_table)
		current_linenode = current_function.start;
		return get_user_input();


	if isinstance(expr, Expression):
		op = expr.op
		if op != None:
			#print('Evaluation with operation:', op);
			if op == '+':
				#print("Evaluating plus operator")
				#print(expr.left, expr.right)
				l = evaluate(expr.left);
				r = evaluate(expr.right)
				#print(l, r)
				#return evaluate(expr.left) + evaluate(expr.right);
				return l + r
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
			elif op == '++':
				# print ("evaluting the ++ operation on the variable", expr.left.left)
				# print (history_table)
				# print ("the value to be assigned is ", evaluate(Expression ('+', expr.left.left, "1")))
				Assignment(expr.left.left, Expression('+', expr.left.left, "1")).process()
				# print("Increment complete")

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

	elif line_info['type'] == 'for_loop':
		initial = get_expression(line_info['value']['initialization'])
		cond = get_expression(line_info['value']['condition'])
		updater = get_expression(line_info['value']['operation'])
		body = get_flow_graph (line_info['value']['body'])

		return ForLoop(initial, cond, updater, body)

	if line_info['type'] == 'return':
		expr = line_info['value']['expression']
		return ReturnStatement(get_expression(expr))
	if line_info['type'] == 'printf':
		val = line_info['value']
		if isinstance(val, str):
			return PrintfStatement(printf_type = 'str', val = val)
		else:
			if 'float' in val:
				return PrintfStatement(printf_type = 'float', val = get_expression(val['float']))
			elif 'digit' in val:
				return PrintfStatement(printf_type = 'int', val = get_expression(val['digit']))
	if line_info['type'] == 'expr_line':
		expr = line_info['value']['expression'];
		return ExpressionLine(get_expression(expr))


def get_flow_graph(body):
	line_prev = None 
	line_start = None;
	for line_info in body:
		lineno = line_info['span'][0];
		optype = get_op(line_info);
		cur_line_node = LineNode(lineno, optype);
		#print(cur_line_node)
		if isinstance(cur_line_node.optype, IfClause) or isinstance(cur_line_node.optype, ForLoop):
			#print('prev_line: ' + str(cur_line_node))
			cur_line_node.optype.body[1].next = cur_line_node;
		cur_line_node.next = None;
		#print(cur_line_node);
		if line_prev != None:
			#print('prev_line' + str(line_prev))
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
	if ERRORS:
		for error in ERRORS:
			print("Syntax error on line", error[0], ':' + error[1]) 
		exit()
	for i in range(len(AST)):
		print(AST[i])
		init_function(AST[i]);
	global current_linenode;
	current_linenode = function_table['main'].start;

def get_to_next_linenode(isReturn = False):
	global current_linenode, symbol_table, memory_table, history_table
	if isReturn:#when coming from a return statement
		if len(return_node_stack) == 0:
			current_linenode = None
			return
		else:
			#print('Returning to:', return_node_stack[-1])
			current_linenode = return_node_stack.pop();
			return
		return
	if current_linenode == None:#when it is none, but there could some node saved in the return stack
		# print("we got here")
		if len(return_node_stack) == 0:
			current_linenode = None
			return
		else:
			while len(scope_stack) and scope_stack[-1] == 1:
				symbol_table_stack.pop()
				#revert_history_table();
				history_table_stack.pop()
				scope_stack.pop();
			if len(symbol_table_stack):
				symbol_table = symbol_table_stack.pop()
				history_table = history_table_stack.pop()
				#revert_history_table();
				scope_stack.pop();
				#print('Scope stack after:', scope_stack);
				prev_size = memory_table_stack.pop()
				memory_table = memory_table[:prev_size]
			current_linenode = return_node_stack.pop();		
			return
	if current_linenode.next != None:
		#print(current_linenode)
		current_linenode = current_linenode.next
		if isinstance(current_linenode.optype, IfClause):
			if current_linenode.optype.visited:
				#print(current_linenode)
				current_linenode.optype.visited = False
				scope_stack.pop();
				current_linenode = current_linenode.next
				#global symbol_table
				symbol_table = symbol_table_stack.pop();
				revert_history_table();
				return
		return
	else:
		if len(return_node_stack) == 0:
			current_linenode = None
		else:
			#print('Returning to:', return_node_stack[-1])
			# print('we are here 3')
			while len(scope_stack) and scope_stack[-1] == 1:
				symbol_table_stack.pop()
				#revert_history_table();
				history_table_stack.pop()
				scope_stack.pop();
			if len(symbol_table_stack):
				symbol_table = symbol_table_stack.pop()
				history_table = history_table_stack.pop()
				#revert_history_table();
				scope_stack.pop();
				#print('Scope stack after:', scope_stack);
				prev_size = memory_table_stack.pop()
				memory_table = memory_table[:prev_size]
			current_linenode = return_node_stack.pop();



def get_user_input():
	# global current_linenode
	# print(current_linenode);
	# print('Symbol table', symbol_table);
	# print('Symbol table stack', symbol_table_stack);
	# print('Memory table', memory_table);
	# print('History table', history_table);
	# print('History table stack', history_table_stack);
	# print('Return node stack');	
	# for return_node in return_node_stack:
	# 	print(return_node);
	# print('done')
	global next_cnt;
	endcheck = False;
	if current_linenode != None:
		if show_line_info == 'n':
			pass
		else:
			print('Line '+ str(current_linenode.lineno) + ':' + code_lines[current_linenode.lineno - 1])
	else:
		print('End of program');
		endcheck = True
		next_cnt = 0;
	while next_cnt:
		#print('we are here with + next cnt')
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
		return get_user_input();
	elif user_cmd[0] in ['print', 'p', 'trace', 't']:
		while len(user_cmd) and user_cmd[0] in ['print', 'p', 'trace', 't']: 
			if len(user_cmd) <= 1:
				print("Command needs one parameter");
			else:
				if user_cmd[0] == 'print' or user_cmd[0] == 'p':
					print(lookup_value(user_cmd[1]))
				elif user_cmd[0] == 'trace' or user_cmd[0] == 't':
					print(trace(user_cmd[1]), end = '')
			user_inp = input().strip();
			user_cmd = user_inp.split();
	if len(user_cmd) == 0:
		return get_user_input();
	if (endcheck):
		exit();
	if user_cmd[0] in ['next', 'n']:
		#global next_cnt
		next_cnt = 1;
		if len(user_cmd) > 1:
			#print(user_cmd[1])
			if user_cmd[1].isdigit():
				next_cnt = int(user_cmd[1]);
			else:
				print("Incorrect command usage: try 'next [lines]'")
				next_cnt = 0;
				return
		while (next_cnt):
			if (current_linenode == None):
				return;
			while not isinstance(current_linenode.optype, ReturnStatement):
				interpreter();
				#print('symbol_table', symbol_table)
				return get_user_input();
			if isinstance(current_linenode.optype, ReturnStatement):
				# print('IT IS A RETURN STATEMENT', current_linenode);
				return interpreter();
			#else:
			#	interpreter();
			#current_linenode.optype.process();
			# get_to_next_linenode();
	elif (user_cmd[0] in ["help", "h"]):
		print(available_commands)
	elif (user_cmd[0] in ["quit", "q", "exit"]):
		print("Exiting debugger")
		exit()
	else:
		global no_of_invalid_commands
		if (no_of_invalid_commands >= 2):
			print(available_commands)
			no_of_invalid_commands = 0
		else:
			no_of_invalid_commands+=1
			get_user_input()
			

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
	# print('Return_node_stack:', return_node_stack);
	# print('isReturn', isReturn);
	if isReturn:
		# print("returning", rax)
		return rax;
	
	

def start_interpreter():
	global current_linenode, symbol_table, show_line_info
	while (not show_line_info in ['y', 'n']):
		show_line_info = input("Do you want to see the line which is to be executed?\nFor example: Line 3: float total;\nenter 'y' for yes or 'n' for no\n")
	print(available_commands)
	while current_linenode != None:
		get_user_input();
		
	# while get_user_input():
	# 	pass;


init_interpreter();
#function_walk('main')
start_interpreter();
#function_walk('main');

		

	




