default:
	yacc -d mini_c.y
	lex mini_c.l
	cc -c lex.yy.c y.tab.c -w
	cc -o mini_c lex.yy.o y.tab.o -lfl -w
	rm lex.yy.c lex.yy.o y.tab.c y.tab.o
