#just takes in the whole program and turns it into a string and sends it down
#probably not the most memory effecient way to do it.
import sys, lexer, parser, codegen

in_file = open(sys.argv[1], "r")

in_str = in_file.read()

in_file.close()

lex = lexer.Lex(in_str)

tokens = lex.lex()

print(tokens)

par = parser.Parser(tokens)

ast = par.parse()

print(ast)

try:
    cdg = codegen.Codegen(sys.argv[2], ast)
except IndexError:
    cdg = codegen.Codegen("a.out", ast)

cdg.codegen()

cdg.close()


