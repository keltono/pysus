import ast

"""
formal(ish) grammar

<toplevel> ::= EMPTY
             | <function> <toplevel>

<function> ::= def <type> ID"("<arg-list-pre>")" "{" <stmnt-list> "}"

<stmnt-list> ::= EMPTY
               | <stmnt> ";" <stmnt-list>

<stmnt> ::= "let" <type> ID "=" <expr>
           |"var" <type> ID "=" <expr>
           |ID = <expr>
           |"if" "(" <expr> ")" "{" <stmnt-list> "}"
           |"return" <expr>
           |<expr> #allows calls


<expr-list> ::= <expr> <expr-list-post>
              | EMPTY

<expr-list-post> ::= , <expr> <expr-list-post>
                   | EMPTY

<expr> ::= <compare>

<compare> ::= <add> == <add>
            | <add> < <add>
            | <add> > <add>
            | <add>

<add> ::= <mult> + <mult>
        | <mult> - <mult>
        | <mult>

<mult> ::= <unary> * <unary>
         | <unary> / <unary>
         | <unary>

<unary> ::= -<primary>
          | !<primary>
          | <pimary>

<primary> ::= ID
            | <call>
            | (<expr>)
            | NUM
            | true
            | false

<call> ::= ID(<expr-list>)

<type> ::= "int"
         | "double"
         | "bool"

<arg-list-pre> ::= EMPTY
             | <arg> <arg-list>

<arg-list> ::= EMPTY
             | , <arg> <arg-list>
<arg> ::= <type> ID

"""

class Parser:
    def __init__(self, token_list):
        #I call it a "token list" but its more of a token stack
        self.tl = token_list
        self.previous = token_list[0]
        self.ast_list = []
    def add_ast(self, to_add,to_junk=1):
        self.ast_list.append(to_add)
    def match(self, *args):
        if len(self.tl) == 0:
            return False
        for ty in args:
            if(self.tl[0].type == ty):
                return True
        return False
    def match_val(self, *args):
        if len(self.tl) == 0:
            return False
        for val in args:
            if(self.tl[0].val == val):
                return True
        return False
    def consume(self, cons, err):
        #basically match_val but throws an error if false
        if len(self.tl) == 0:
            raise ValueError(err)
        if self.tl[0].val == cons:
            self.pop()
            return
        raise ValueError(err)

    def pop(self):
        top = self.tl[0]
        self.tl = self.tl[1:]
        self.previous = top
        return top
    def parse(self):
        while(self.tl):
            # try: #TODO(?) add global vars
            if self.match('def'):
                self.pop()
                self.add_ast(self.parse_def())
            #ignore toplevel newlines
            elif self.match_val('\n'):
                self.pop()
            else:
                #going to allow top level exprs for testing reasons
                self.add_ast(self.statementlist("toplevel", 0))
                #raise ValueError
            # except:
            #     print("uknown token {} outside of function!".format(curr))
        return self.ast_list

    #this one starts with "parse_" because def is a reserved word in python. does *not* expect the def keyword
    def parse_def(self):
        #TODO: real type parsing (to handle pointers, arrays)
        if self.match('type'):
            ty = self.pop().val
        else:
            raise ValueError(f'expected function return type in function definition on line {self.tl[0].line}')
        if self.match('ident'):
            name = self.pop()
        else:
            raise ValueError('expected function name in function definition on line {self.tl[0].line}')
        args = self.args(name.val)
        body = self.statementlist("function definition", name.line)
        arg_types = []

        for arg in args:
            arg_types.append(arg[0])

        #TODO properly format type (in the case of pointers/arrays)
        return ast.Def(name.val, ("function",(arg_types,(ty,None))), args, body)

    #expects and consumes curly braces (e.g {<stmntlist>} )
    def statementlist(self,parent, line):
        stmntlist = []
        while self.match_val('\n'):
            self.pop()
        self.consume('{', "expected '{' " +f" in {parent} " + f" on line {line}")
        #how often i check to see if the token is '}' is bad, but it works!
        while not self.match_val('}'):
            while self.match_val('\n'):
                self.pop()
            if self.match_val('}'):
                break
            stmntlist.append(self.statement())
            if self.match_val('}'):
                break
            if not self.previous.val == '}':
                self.consume('\n', "expected new line after statement on line {self.tl[0].line}")
        self.pop()
        return stmntlist

    def statement(self):
        if self.match("let"):
            line = self.pop().line
            #TODO add proper type parsing (pointers, arrays, custom types, etc)
            if self.match("type"):
                ty = self.pop().val
                if self.match("ident"):
                    name = self.pop().val
                else:
                    raise ValueError(f"expected name in let declaration on line {line}, saw {self.tl[0].val}")
            elif self.match("ident"):
                ty= self.pop().val
                #type inference
                if self.match_val("="):
                    name = ty
                    ty = None
                #this is where more complete type parsing would happen
                #for the time being, just error out
                else:
                    raise ValueError(f"expected type in let declaration on line {line}, saw {self.tl[0].val}")

            else:
                raise ValueError(f"expected type in let declaration on line {line}, saw {self.tl[0].val}")
            self.consume("=", f"expected '=' in let declaration on line {line}, saw {self.tl[0].val}")
            ex = self.expr()
            return ast.Let(name,(ty,None),ex)

        elif self.match("var"):
            line = self.pop().line
            #TODO add proper type parsing (pointers, arrays, custom types, etc)
            if self.match("type"):
                ty = self.pop().val
                if self.match("ident"):
                    name = self.pop().val
                else:
                    raise ValueError(f"expected name in let declaration on line {line}, saw {self.tl[0].val}")
            elif self.match("ident"):
                ty= self.pop().val
                #type inference
                if self.match_val("="):
                    name = ty
                    ty = None
                #this is where more complete type parsing would happen
                #for the time being, just error out
                else:
                    raise ValueError(f"expected type in let declaration on line {line}, saw {self.tl[0].val}")

            else:
                raise ValueError(f"expected type in let declaration on line {line}, saw {self.tl[0].val}")
            self.consume("=", f"expected '=' in var declaration on line {line}, saw {self.tl[0].val}")
            ex = self.expr()
            return ast.Var(name,(ty,None),ex)
        elif self.match("if"):
            line = self.pop().line
            ex = self.expr()
            thenstmnts = self.statementlist("if statement",line)
            if not self.match("else"):
                elsestmnts = None
            else:
                line = self.pop().line
                elsestmnts = self.statementlist("else statement", line)
            return ast.If(ex,thenstmnts,elsestmnts)
        elif self.match('return'):
            self.pop()
            returning = self.expr()
            return ast.Return(returning)
        elif self.match('ident') and self.tl[1].val == '=':
            name = self.pop().val
            self.pop()
            val = self.expr()
            return ast.Assign(name, val)
        else:
            return self.expr()

    #logic for parsing exprs. each function represents a grammar (or two) spesified above.
    #these multiple function deal with order of operations. lowest down in the chain (unary,mult) have highest precedence.
    def expr(self):
        expr = self.compare()
        while(self.match_val('==','!=')):
            op = self.pop().val
            rhs = self.compare()
            expr = ast.Binary(expr, op, rhs)
        return expr

    def compare(self):
        expr = self.add()
        while(self.match_val('>', '<', '<=', '>=')):
            op = self.pop().val
            rhs = self.add()
            expr = ast.Binary(expr, op, rhs)
        return expr

    def add(self):
        expr = self.mult()
        while(self.match_val('+', '-')):
            op = self.pop().val
            rhs = self.mult()
            expr = ast.Binary(expr, op, rhs)
        return expr

    def mult(self):
        expr = self.unary()
        while(self.match_val('/','*')):
            op = self.pop().val
            rhs = self.unary()
            expr = ast.Binary(expr, op, rhs)
        return expr

    def unary(self):
        if(self.match_val('-','!')):
            op = self.pop().val
            return ast.unary(op, unary())
        return self.primary()

    def primary(self):
        if self.match('int'): #this counts for ints and longs
            i = self.pop().val
            return (ast.Literal(i))
        elif self.match('float'): #counts for floats and doubles
            f = self.pop().val
            return (ast.Literal(f))
        elif self.match('true'):
            self.pop()
            return ast.Literal(True)
        elif self.match('false'):
            self.pop()
            return (ast.Literal(False))
        elif self.match('ident'):
            name = self.pop().val
            if(self.match_val('(')):
                #name is passed for error reporting
                arg_list = self.tuple(name)
                return ast.Call(name, arg_list)
            return ast.Variable(name)
        elif self.match_val('('):
            line_num = self.pop().line
            expr = self.expr()
            self.consume(')', f"missing ')' in '('<expr>')' on line {line_num}")
            return expr
        else:
            tok = self.pop()
            raise ValueError(f"invalid token '{tok.val}' in expr on line {tok.line}")
    #TODO args, parse_def

    #not sure how to differentiate between '('<expr>')' and a tuple in parsing...
    #I guess you just have to iterate over all of the tokens between the parens and see if there's a comma.
    #parses the insides of a tuple, returning a list of the values. used in parsing tuples and function calls. expects the opening paren '('. consumes the closing paren ')'
    def tuple(self,name):
        vals = []
        if not self.match_val('('):
            raise ValueError(f'expected "(" in {name} function call on line {self.tl[0].line}')
        else:
            self.pop()
        while(not self.match_val(')')):
            vals.append(self.expr())
            if(self.match_val(',')):
                self.pop()
            else:
                break
        if(not self.match_val(')')):
            raise ValueError(f'invalid token in function call {name} on line {self.tl[0].line}')
        self.pop()
        return vals
    #parses arguments in a function definition (e.g type name, type1 name1, ...) same as above where it expects the opening paren and consumes the closing paren
    #returns a list of string tuples. in the form [(type,name),(type1,name1)]
    def args(self,name):
        arg_list = []
        if not self.match_val('('):
            raise ValueError(f'expected "(" in {name} function definition on line {self.tl[0].line}')
        else:
            self.pop()
        while(not self.match_val(')')):
            if self.match('type'):
                ty = self.pop()
            else:
                raise ValueError(f"expected type in {name} function definition, saw {self.tl[0].val} on line {self.tl[0].line}")
            if self.match('ident'):
                arg_list.append(((ty.val,None),self.pop().val))
            else:
                raise ValueError(f"expected arg name in {name} function definition, saw {self.tl[0].val} on line {self.tl[0].line}")
            if(self.match_val(',')):
                self.pop()
            else:
                break
        if(not self.match_val(')')):
            raise ValueError(f'invalid token in function definition {name} on line {self.tl[0].line}')
        self.pop()
        return arg_list

    def __str__(self):
        return (f"{self.ast_list}")
