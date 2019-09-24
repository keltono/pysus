#takes a string, returns a list of tokens
#This implimentation is much nicer than the ocaml version. Flexibility in using imperative progamming ocasionally and never using camlp4 parsers is nice.
from token import Token

class Lex:
    def __init__(self, in_str):
        self.token_list = []
        self.in_str = in_str

    def junk(self):
        self.in_str = self.in_str[1:] #returns the cdr of a seq

    def lex(self):
        if len(self.in_str) == 0:
            return self.token_list
        ch = self.in_str[0]
        if ch == ' ' or ch == '\n' or ch == '\r' or ch == '\t' : #all of these just add to the token list. do not return anything.
            self.junk() #trash white space
            self.lex()

        elif ch == '/':
            self.junk()
            if (not self.in_str) or self.in_str[0] != '/':
                self.token_list.append(Token('kwd','/'))
            else:
                self.junk()
                self.lex_comment()

        elif ch == '+': #TODO add +=
            self.junk()
            self.token_list.append(Token('kwd', '+')) #all of these just add to the token list and don't return anything

        elif ch == '-': #these only exist for the purpose of being extended later (e.g +=, *=). the current system would treat it this way by default
            self.junk()
            self.token_list.append(Token('kwd', '-'))

        elif ch == '*':
            self.junk()
            self.token_list.append(Token('kwd', '*')) #always count this as binop? not sure.

        elif ch == '%':
            self.junk()
            self.token_list.append(Token('kwd', '%'))

        elif ch == '<':
            self.junk()
            if len(self.in_str) == 0:
                self.token_list.append(Token('kwd', '<'))
            else:
                if self.in_str[0] == '=':
                    self.junk()
                    self.token_list.append(Token('binop', '<='))
                else:
                    self.token_list.append(Token('kwd', '<'))

        elif ch == '>':
            self.junk()
            if len(self.in_str) == 0:
                self.token_list.append(Token('kwd', '>'))
            else:
                if self.in_str[0] == '=':
                    self.junk()
                    self.token_list.append(Token('binop', '>='))
                else:
                    self.token_list.append(Token('kwd', '>'))

        elif ch == '=':
            self.junk()
            if len(self.in_str) == 0:
                self.token_list.append(Token('kwd', '='))
            else:
                if self.in_str[0] == '=':
                    self.junk()
                    self.token_list.append(Token('binop', '=='))
                else:
                    self.token_list.append(Token('kwd', '='))

        elif ch.isnumeric() or ch == ".":
           self.lex_number()

        elif ch.isalpha() or ch == '_':
            self.lex_ident()
        else:
            self.junk()
            self.token_list.append(Token("kwd", ch))
        return self.lex()

    def lex_ident(self):
        buff = ""
        while(( self.in_str[0].isalpha() or self.in_str[0] == '_') and self.in_str ):
            buff += self.in_str[0]
            self.junk()
        if buff == 'def':
            self.token_list.append(Token('def'))
        elif buff == 'return':
            self.token_list.append(Token('return'))
        elif buff == 'extern':
            self.token_list.append(Token('extern'))
        elif buff == 'if':
            self.token_list.append(Token('if'))
        elif buff == 'else':
            self.token_list.append(Token('else'))
        elif buff == 'let':
            self.token_list.append(Token('let'))
        elif buff == 'var': #TODO maybe go back to point?
            self.token_list.append(Token('var'))
        elif buff == 'true':
            self.token_list.append(Token('true'))
        elif buff == 'false':
            self.token_list.append(Token('false'))
        elif buff == 'int':
            self.token_list.append(Token('type','int'))
        elif buff == 'float':
            self.token_list.append(Token('type','float'))
        elif buff == 'char':
            self.token_list.append(Token('type','char'))
        else:
            self.token_list.append(Token('ident', buff))
       #TODO: add: and, or for, null

    def lex_number(self): #these also just add to the token list directly
        buff = ''
        while((self.in_str[0].isnumeric() or self.in_str[0] == '.') and self.in_str ):
            buff += self.in_str[0]
            self.junk()
        if "." in buff: #TODO: check if there is more than 1 '.' in the buff
            self.token_list.append(Token("float", float(buff)))
        else:
            self.token_list.append(Token("int", int(buff)))

    def lex_comment(self):
        while(self.in_str != '\n' and self.in_str != '\r'):
            self.junk()

    def __str__(self):
        return ("{}".format(self.token_list))






