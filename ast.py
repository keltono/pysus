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
        -While
        -Return
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
    def __repr__(self):
        return f"({self.op}{self.operand.__repr__()})"
#TODO: add ternaries

class Variable(Expr):
    def __init__(self, name):
        self.name= name
    def __repr__(self):
        return f"(var: {self.name})"
    def __str__(self):
        return f"(var: {self.name})"

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
    def __repr__(self):
        s=""
        for arg in self.args:
            s +=f", {arg}"
        s = s[2:]
        return f"def {self.type} {self.name}({s}) {self.body}"
    def __str__(self):
        s=""
        for arg in self.args:
            s +=f", {arg}"
        s = s[2:]
        return f"def {self.type} {self.name}({s}) {self.body}"

class Return(Statement):
    def __init__(self,returning):
        self.returning = returning
    def __repr__(self):
        return f"return {self.returning}"

class Let(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.val = val
    def __str__(self):
        return f"let {self.type} {self.name} = {self.val}"
    def __repr__(self):
        return f"let {self.type} {self.name} = {self.val}"

class Var(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type
        self.val = val
    def __str__(self):
        return f"var {self.type} {self.name} = {self.val}"
    def __repr__(self):
        return f"var {self.type} {self.name} = {self.val}"

class Assign(Statement): #for re assignment of a var. doesn't make sense for it to be an expr now
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self):
        return f"{self.lhs} = {self.rhs}"

class If(Statement):
    def __init__(self, condition, thenbody, elsebody=None):
        self.condition = condition
        self.thenbody = thenbody
        self.elsebody = elsebody
    def __repr__(self):
        return f"if({self.condition}) {self.thenbody} else {self.elsebody} "
class While(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"while ({self.condition}) {self.body}"
class For(Statement):
    def __init__(self, ident, type, cond, inc, body):
        self.id = ident
        self.type = type
        self.cond = cond
        self.inc = inc
        self.body = body #stmntList ideally




