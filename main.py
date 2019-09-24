#just takes in the whole program and turns it into a string and sends it down
#probably not the most memory effecient way to do it.
import sys, lexer

in_file = open(sys.argv[1], "r")

in_str = in_file.read()


lex = lexer.Lex(in_str)

print(lex.lex())



