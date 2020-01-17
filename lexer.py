#takes a string, returns a list of tokens
#This implimentation is much nicer than the ocaml version. Flexibility in using imperative progamming ocasionally and never using camlp4 parsers is nice.
from token import Token

class Lex:
    def __init__(self, in_str):
        self.token_list = []
        self.in_str = in_str
        self.lineno = 1

    def junk(self):
        self.in_str = self.in_str[1:] #returns the cdr of a seq

    def add(self, ty, val=None):
        if(val != None):
            self.token_list.append(Token(ty,val,self.lineno))
        else:
            self.token_list.append(Token(ty,line=self.lineno))


    def lex(self):

        while(len(self.in_str) != 0):
            ch = self.in_str[0]
            if ch == '\n':
                self.lineno += 1
                self.add('newline','\n')
                self.junk()
            elif ch == ' ' or ch == '\r' or ch == '\t' :
                self.junk() #trash white space
            elif ch == '/':
                self.junk()
                if (not self.in_str):
                    self.add('kwd','/')
                else:
                    if self.in_str[0] == '/':
                        self.junk()
                        self.lex_comment()
                    elif self.in_str[0] == '*':
                        self.junk()
                        self.lex_multi_comment()
                    else:
                        self.add('kwd','/')


            elif ch == '+': #TODO add +=
                self.junk()
                self.add('kwd', '+') #all of these just add to the token list and don't return anything

            elif ch == '-': #these only exist for the purpose of being extended later (e.g +=, *=). the current system would treat it this way by default
                self.junk()
                self.add('kwd', '-')

            elif ch == '*':
                self.junk()
                self.add('kwd', '*')

            elif ch == '%':
                self.junk()
                self.add('kwd', '%')

            elif ch == '<':
                self.junk()
                if len(self.in_str) == 0:
                    self.add('kwd', '<')
                else:
                    if self.in_str[0] == '=':
                        self.junk()
                        self.add('kwd', '<=')
                    else:
                        self.add('kwd', '<')

            elif ch == '>':
                self.junk()
                if len(self.in_str) == 0:
                    self.add('kwd', '>')
                else:
                    if self.in_str[0] == '=':
                        self.junk()
                        self.add('kwd', '>=')
                    else:
                        self.add('kwd', '>')
            elif ch == '!':
                self.junk()
                if len(self.in_str) == 0:
                    self.add('kwd', '!')
                else:
                    if self.in_str[0] == '=':
                        self.junk()
                        self.add('kwd', '!=')
                    else:
                        self.add('kwd', '!')

            elif ch == '=':
                self.junk()
                if len(self.in_str) == 0:
                    self.add('kwd', '=')
                else:
                    if self.in_str[0] == '=':
                        self.junk()
                        self.add('kwd', '==')
                    else:
                        self.add('kwd', '=')
            #TODO: add strings and chars

            elif ch.isnumeric() or ch == ".":
               self.lex_number()

            elif ch.isalpha() or ch == '_':
                self.lex_ident()
            else:
                self.junk()
                self.add("kwd", ch)
        return self.token_list

    def lex_ident(self):
        buff = ""
        while(( self.in_str[0].isalpha() or self.in_str[0] == '_' or self.in_str[0].isnumeric()) and self.in_str ):
            buff += self.in_str[0]
            self.junk()
        if buff == 'def':
            self.add('def')
        elif buff == 'return':
            self.add('return')
        elif buff == 'extern':
            self.add('extern')
        elif buff == 'while':
            self.add('while')
        elif buff == 'if':
            self.add('if')
        elif buff == 'else':
            self.add('else')
        elif buff == 'let':
            self.add('let')
        elif buff == 'var': #TODO maybe go back to point?
            self.add('var')
        elif buff == 'true':
            self.add('true')
        elif buff == 'false':
            self.add('false')
        elif buff == 'int':
            self.add('type','int')
        elif buff == 'float':
            self.add('type','float')
        elif buff == 'char':
            self.add('type','char')
        elif buff == 'bool':
            self.add('type','bool')
        elif buff == 'long':
            self.add('type','long')
        else:
            self.add('ident', buff)
       #TODO: add: and, or, for, null

    def lex_number(self): #these also just add to the token list directly
        buff = ''
        while((self.in_str[0].isnumeric() or self.in_str[0] == '.') and self.in_str ):
            buff += self.in_str[0]
            self.junk()
        if "." in buff:
            if buff.count('.') > 1:
                print("error! more than 1 period in number!") #TODO error handle for real
            else:
                #this casting should probably happen in the parser, but meh
                self.add("float", float(buff))
        else:
            self.add("int", int(buff))

    def lex_comment(self):
        while(self.in_str[0] != '\n' and self.in_str[0] != '\r'):
            self.junk()
    def lex_multi_comment(self):
        while(self.in_str[0] != '*' and self.in_str[1] != '/'):
            self.junk()
        self.in_str = self.in_str[2:]
    def __str__(self):
        return ("{}".format(self.token_list))
