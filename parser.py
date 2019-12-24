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
        self.ast_list = []
    def add_ast(self, to_add,to_junk=1):
        self.ast_list.append(to_add)
        #TODO: see if i need to pop here (WHAT IS POPPING)
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
        return top
    def parse(self):
        while(self.tl):
            # try: #TODO(?) add global vars
            if self.match('def'):
                self.add_ast(self.parse_def())
            else:
                #going to allow top level exprs for testing reasons
                self.add_ast(self.expr())
                #raise ValueError
            # except:
            #     print("uknown token {} outside of function!".format(curr))

    #logic for parsing exprs. each function represents a grammar (or two) spesified above.
    def expr(self):
        return self.equal()

    #these multiple function deal with order of operations. lowest down in the chain (unary,mult) have highest precedence.
    def equal(self):
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
        if self.match('int'):
            i = self.pop().val
            return (ast.Literal(i))
        elif self.match('float'):
            f = self.pop().val
            return (ast.Literal(f))
        elif self.match('true'):
            self.pop()
            return ast.Literal(True)
        elif self.match('false'):
            self.pop()
            return (ast.Literal(False))
        elif self.match('ident'):
            name = self.pop()
            if(self.match_val('(')):
                self.pop()
                #name is passed for error reporting
                arg_list = self.arg_vals(name)
                self.consume(')', f"missing ')' at end of {name.val} call on line {name.line}")
                return ast.Call(name.val, arg_list)
            return ast.Variable(name.val)
        elif self.match_val('('):
            line_num = self.pop().line
            expr = self.expr()
            self.consume(')', f"missing ')' in '('<expr>')' on line {line_num}")
            return expr
        else:
            tok = self.pop()
            raise ValueError(f"unrecognized token '{tok.val}' in expr on line {tok.line}")
    #TODO args, parse_def

    #arg_vals is for the arguments given to a call, args is for the arguments given to a function definition
    def arg_vals(self,name):
        arg_list = []
        while(not self.match_val(')')):
            arg_list.append(self.expr())
            if(self.match_val(',')):
                self.pop()
            else:
                break
        if(not self.match_val(')')):
            raise ValueError('invalid token in function call {name} one line {self.tl[0].line}')
        return arg_list


    def __str__(self):
        return ("{}".format(self.ast_list))
