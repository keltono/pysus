#just takes in the whole program and turns it into a string and sends it down
#probably not the most memory effecient way to do it.
import sys, lexer

in_file = open(sys.argv[1], "r")

in_str = in_file.read()

n_file.close()

lex = lexer.Lex(in_str)

tokens = lex.lex()

print(tokens)



