"""
summary:
Ast:
    Expr:
        -Literal
        -Binary
        -Unary
        -Call
        -Variable
    Statement:
        -Let
        -Var
        -Assign
        -If
        -For
        -StatementList
"""

class Ast:
    pass
class Expr(Ast):
    #Anything that *does* yield a value.
    pass
class Statement(Ast):
    #anything that doesn't yield a value directly. loops, declarations, return statements, etc
    pass

class Literal(Expr):
    #Numbers, bools, strings, oh my!
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return str(self.val)
    def __str__(self):
        return str(self.val)

class Binary(Expr):
    def __init__(self, lhs, op, rhs):
        #probably should have gone with a statically typed language... this is worryingly easy
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self):
        return f"({self.lhs.__repr__()} {self.op} {self.rhs.__repr__()})"
    def __str__(self):
        return f"({self.lhs.__repr__()} {self.op} {self.rhs.__repr__()})"

class Unary(Expr):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
#TODO: add ternaries

class Variable(Expr):
    def __init__(self, name):
        self.name= name

class Call(Expr):
    def __init__(self, name, args):
        self.name= name
        self.args = args
    def __repr__(self):
        s = ""
        for arg in self.args:
            s +=f", {arg}"
        s = s[2:]
        return f"{self.name}({s})"
class Def(Statement):
    def __init__(self, name, type, args, body):
        self.name= name
        self.type= type
        self.args = args
        self.body = body

class Let(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.val = val
class Var(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.val = val

class Assign(Statement): #for re assignment of a var. doesn't make sense for it to be an expr now
    def __init__(self, var, val):
        self.var = var
        self.val = val

class If(Statement):
    def __init__(self, condition, thenbody, elsebody):
        self.condition = condition
        self.thenbody = thenbody
        self.elsebody = elsebody
class For(Statement):
    def __init__(self, ident, type, cond, inc, body):
        self.id = ident
        self.type = type
        self.cond = cond
        self.inc = inc
        self. body = body #stmntList ideally

class Arg(Statement):
    def __init__(self, name, type=None):
        self.type = type
        self.name = name



