import ast
class Parser:
    def __init__(self, token_list):
        self.tl = token_list
        self.ast_list = []
        binop_prec = { #could put this in main.py but doesn't really seem necessary
        #TODO  <- and/or  ->
        '||' : (7, 'bool'),
        '&&' : (8, 'bool'),
        '==' : (9, 'any'),
        '!=' : (9, 'any'),
        '<=' : (10, 'any'),
        '>=' : (10, 'any'),
        '<' : (10, 'any'),
        '>' : (10, 'any'),
        '+' : (20, 'any'),
        '-' : (20, 'any'),
        '%' : (30, 'any'),
        '*' : (40, 'any'),
        '/' : (40, 'any'),
        }

    def junk(self, num=1):
        self.tl = self.tl[num:]
    def add(self, to_add,to_junk=1):
        self.tl.append(to_junk)
        self.junk(to_junk)
    def parse(self):
        while(self.tl):
            try: #TODO? add global vars
                if self.tl[0].type == 'def':
                    self.junk()
                    self.add(self.parse_def())
                elif self.tl[0].type == 'extern':
                    self.junk()
                    self.add(self.parse_extern())
                else: #TODO have this raise an error. parses primary for testing purposes.
                    self.add(parse_expr())
                    # raise ValueError
            except:
                print("uknown token {} outside of function!".format(tok)) #TODO modify if I add classes
    def parse_primary(self): #returns the AST
        if self.tl[0].type == 'int': #primary here just means Expr - unary and binary (and ternary when that comes)
            self.junk()
            return (ast.Int(self.tl[0].val))
        elif self.tl[0].type == 'float':
            self.junk()
            return (ast.Float(self.tl[0].val))
        elif self.tl[0].type == 'true':
            self.junk()
            return ast.Bool(True)
        elif self.tl[0].type == 'false':
            self.junk()
            return (ast.Bool(False))
        #TODO add '(' expr ')' here
        elif self.tl[0].type == 'ident': #variables and calls
            name = self.tl[0].val
            if self.tl[1].val=='(':
                self.junk(2) #TODO return an ast.Call() here
                # arg_list = self.parse_args(False) TODO
            else:
                self.junk()
                return (ast.Variable_ref(name))
        return args

    #TODO add parse_unary
    def parse_expr(self): #bascially primary + binop possibility:
        lhs = parse_primary() #this works because '(' expr ')' is in parse primary. the code in parse_rhs allows for 1 + 1 + 1 etc.
        #no need to match because primary already junks
        ch  = self.tl[0]
        if(ch.type == 'kwd' and ch.val in binop_prec ):
            if
        else:
            return lhs

        pass

    def parse_def(self):
        #TODO
        print("saw a def!")
        self.junk()
    def parse_extern(self):
        #TODO
        print("saw an extern!")

'''    def parse_args(self, named_args):
        args = []
        while(True):
            if named_args:
                if self.tl[0].type == 'type' and self.tl[1].type == 'ident':
                    args += ast.Arg(self.tl[1].val, self.tl[0].val)  #name, type
                elif self.tl[0].type == 'ident':
                    print("Error: expected type in argument, got: ".format(self.tl[0]))
                    raise RuntimeError
                elif self.tl[0].val == ')':
                    break
                else:
                    print("Error: invalid argument at token {}".format(self.tl[0]))
                    raise RuntimeError
            else:
                if self.tl[0].type != 'ident' or self.tl[0].type == 'int' or self.t[0].type == 'float' or self.tl[0] != 'true' or self.tl[0] != 'false':  #TODO: extend
                    print("Error: invalid argument at token {}".format(self.tl[0]))
                    raise RuntimeError
                elif self.tl[0].val == ')':
                    break
                else:
                    args += Arg(self.tl[0].val) #parse_expr
'''

