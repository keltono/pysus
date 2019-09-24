"""
summary:
Ast:
    Expr:
        Atomic:
            -Int
            -Float
            -Char
            -Bool
        -Variable
        -Binary
        -Unary
        -Call
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
    pass
class Statement(Ast): #anything that doesn't yield a value directly. loops, declarations, return statements, etc
    pass

class Atomic(Expr): #base types
    def __init__(self, val):
        self.val = val

class Int(Atomic):
    def __init__(self, val):
        super().__init__(self, val)

class Float(Atomic)
    def __init__(self, val):
        super().__init__(self, val)

class Char(Atomic)
    def __init__(self, val):
        super().__init__(self, val)

class Bool(Atomic)
    def __init__(self, val):
        super().__init__(self, val)

class Variable(Expr) #variable ref. stores name of var which is dealt with in codegen.
    def __init__(self, val):
        super().__init__(self, val)

class Binary(Expr):
    def __init__(self, op, lhs, rhs):
        self.op = op #the lack of types here makes this worryingly easy
        self.lhs = lhs
        self.rhs = rhs

class Unary(Expr):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
#TODO: add ternaries

class Call(Expr):
    def __init__(self, name, args):
        self.name= name

class Let(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type #not sure how to represent type here. for now a string will do but TODO add working arrays
        self.val = val
class Var(Statement):
    def __init__(self, name, type, val):
        self.name = name
        self.type = type #not sure how to represent type here. for now a string will do but TODO add working arrays
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

class StatementList(Statement):
    def __init__(self, stmntList):
        self.statements = stmntList


