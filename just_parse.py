import sys, lexer, parser, codegen

in_file = open(sys.argv[1], "r")

in_str = in_file.read()

in_file.close()

lex = lexer.Lex(in_str)

tokens = lex.lex()

par = parser.Parser(tokens)

ast = par.parse()

print(ast)
