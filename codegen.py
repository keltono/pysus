#this file handles the actual creation of IR based on input, emmiter.py handles the logic of emmiting IR
#i.e emmiter.py replaces the llvm library, and codegen.py does what it says on the tin
#well, kind of. codegen.py handles a lot of what the llvm library handles, emmiter.py really just handles the admin that comes with complex programs#the actual logic for deciding what line to write is here.

import ast
import emmiter
from value import Value

class Codegen:
    def __init__(self,fd,ast):
        #the emmiter object. This is used a lot and therefore is shortened down
        self.e = emmiter.Emmiter(fd)
        self.ast = ast

    def codegen(self):
        for astNode in self.ast:
            t = type(astNode)
            if t == ast.Def:
                self.codegenDef(astNode)
            else:
               #only defs at the top level for now. I'll probably allow global variables at some point.
               raise ValueError(f"Expected a function defintion on the top level, saw {astNode}")

    #takes in an ast.Def object, emmits, returns nothing
    def codegenDef(self,d):

        #TODO support nested functions. they'll have to be generated outside of the function somehow
        #not totally sure how to handle that given the recusive-desent-esq control flow.
        #probably just something like a list of things that need to be genrated next, that's referenced after a function is generated.
        self.e.scopeUp(d.name, isFunction = True)
        self.e.setIndent(-1)

        self.e.addGlobal(d.name,"@"+d.name,self.e.typeToLLType(d.type), "function", False)
        defline = f"define {self.e.typeToLLType(d.type[1][1])} @{d.name}("
        #args are stored as tuples in the form (type,name)
        #where type is a tuple of ("typeName",info)
        #(covered more in depth in emmiter.py)
        if d.args != []:
            llname = self.e.getName()
            lltype = self.e.typeToLLType(d.args[0][0])
            self.e.addVariable(d.args[0][1], llname, lltype, "arg")
            defline +=f"{lltype} %{llname}"
            d.args = d.args[1:]
            for arg in d.args:
                llname = self.e.getName()
                lltype = self.e.typeToLLType(arg[0])
                self.e.addVariable(arg[1], llname, lltype)
                defline +=f", {lltype} %{llname}"
        defline +=") {"
        self.e.emmit(defline)
        self.e.emmitLabel("entry")
        self.e.setIndent(0)
        self.codegenStatementList(d.body)
        self.e.scopeDown()
        self.e.emmit("}\n")

    def codegenStatementList(self, l):
        if l != None:
            for statement in l:
                self.codegenStatement(statement)
    #doesn't return anything, unlike the codegenExpr
    def codegenStatement(self, s):
        ty = type(s)
        if ty == ast.Return:
            expr = self.codegenExpr(s.returning)

            funcReturnType = self.e.getCurrFuncType()[1]

            if self.canConvert(expr, funcReturnType):
                self.e.emmit(f"ret {funcReturnType} {expr.val}")
            else:
                print(expr.type)
                print(funcLLReturnType)
                raise ValueError(f"return type mismatch in function {self.e.currentScope.name}: expected a(n) {funcReturnType}, saw {expr}")
            #the way I'm doing this right now will basically require me to have a special case for literals *anytime* i use a function

        #lets are scoped to the current function (or the global scope) like var declarations
        #doesn't actually generate any code past the code needed to evaluate the expression,
        #just adds it to the scope so that that value goes in wherever the variable is mentioned
        elif ty == ast.Let:
            #I *could* make it so you can't re-let variables, but where's the fun in that?
            expr = self.codegenExpr(s.val)
            if expr.type[-1] == "*" or expr.category == "var":
                raise ValueError(f"you can't use a let declaration on a pointer dummy! {s}")
            if s.type == None:
                ty = expr.type
            else:
                letLLType = self.e.typeToLLType(s.type)
                if self.canConvert(expr,letLLType):
                    ty = letLLType
                else:
                    #probably shouldn't emmit SSA values in error reporting...
                    raise ValueError(f"Expected a {letLLType} in let delcaration in {self.e.currentScope.name[1]}, saw {expr}")
            self.e.addVariable(s.name, expr.val, ty, "let", expr.isLit)

        elif ty == ast.Assign:
            rhs = self.codegenExpr(s.rhs)
            lhs = self.e.getLLVariable(s.lhs)
            if lhs.category != "var":
                raise ValueError(f"can't re-assign non-var variables. {s}")
            if rhs.isLit:
                if (rhs.type =="i32" or rhs.type == "i1") and lhs.type[0] == "i":
                    rhs.type = lhs.type[:-1]
                elif rhs.type == "double" and lhs.type == "float*":
                    rhs.type = "float"
            if lhs.type != rhs.type +"*":
                raise ValueError(f"type mismatch in assignment {s} lhs: {lhs.type} rhs: {rhs.type}")
            self.e.emmit(f"store {rhs.type} {rhs.val}, {lhs.type} {lhs.val}")

        elif ty == ast.Var:
            expr = self.codegenExpr(s.val)
            if s.type == None:
                ty = expr.type
            else:
                varLLType = self.e.typeToLLType(s.type)
                if self.canConvert(expr, varLLType):
                    ty = varLLType
                else:
                    raise ValueError(f"Expected a {letLLType} in var delcaration in {self.e.currentScope.name[1]}, saw {expr}")
            varName = "%"+self.e.getName()
            self.e.emmit(f"{varName} = alloca {ty}")
            self.e.emmit(f"store {ty} {expr.val}, {ty}* {varName}")
            self.e.addVariable(s.name, varName, ty+"*", "var", expr.isLit)


        elif ty == ast.If:
            cond = self.codegenExpr(s.condition)
            if(cond.type[0] != "i"):
                print(cond.type)
                raise ValueError(f"expected boolean or integer in condition in if statement {s}, saw {cond}")

            #TODO: might need to do some work here to allow pointers and such
            cmpName = "%"+self.e.getName()
            thenName = self.e.getName()+"_then"
            failName = self.e.getName()+"_iffail"
            self.e.emmit(f"{cmpName} = icmp ne {cond.type} {cond.val}, 0")
            self.e.emmit(f"br i1 {cmpName}, label %{thenName}, label %{failName}")
            self.e.emmitLabel(thenName)

            scopeName = self.e.getName()
            self.e.scopeUp(scopeName+"_then",False,increment=False)
            self.codegenStatementList(s.thenbody)
            self.e.scopeDown()

            #ifs, like C, unlike python, have their own scopes.
            if s.elsebody == None:
                self.e.emmit(f"br label {failName}")
                self.e.emmitLabel(failName)
            else:
                doneName = self.e.getName()+"_ifdone"
                self.e.emmit(f"br label %{doneName}")
                self.e.emmitLabel(failName)
                self.e.scopeUp(scopeName+"_else",isFunction=False,increment=False)
                self.codegenStatementList(s.elsebody)
                self.e.scopeDown()
                self.e.emmit(f"br label %{doneName}")
                self.e.emmitLabel(doneName)

        else:
            self.codegenExpr(s)

    #returns a tuple containing the value and the type of the expr
    #e.g ("%example_0x0", "i32")
    #or ("2,"int")
    def codegenExpr(self, ex):
        t = type(ex)
        if t == ast.Literal:
            #TODO string and char literals
            if ex.val == True and type(ex.val) == bool:
                return Value("1","i1","unnamed",True)
            elif ex.val == False and type(ex.val) == bool:
                return Value("0","i1","unnamed",True)
            elif type(ex.val) == float:
                return Value(str(ex.val),"double", "unnamed", True)
            elif type(ex.val) == int:
                return Value(str(ex.val), "i32", "unnamed", True)
            else:
                raise ValueError(f"what the heck is this? I expected a literal of *some kind* but i saw {ex.val} in {ex}")
        #Variable reference, not a var declaration. returns a NamedValue object
        elif t == ast.Variable:
            var = self.e.getLLVariable(ex.name)
            if var.category == "let":
                return var
            elif var.category == "var":
                loadName = "%"+self.e.getName()
                #take off a pointer level
                loadType = var.type[:-1]
                self.e.emmit(f"{loadName} = load {loadType}, {var.type} {var.val}")
                #TODO see if calling both the var pointer and the var result "var" causes issues
                return Value(loadName, loadType, "var", False)
        elif t == ast.Binary:
            #left recursion is fine here because eventually lhs won't be an binary expression
            lhs = self.codegenExpr(ex.lhs)
            rhs = self.codegenExpr(ex.rhs)

            if self.canConvert(lhs,rhs.type):
                ty = rhs.type
            elif self.canConvert(rhs, lhs.type):
                ty = lhs.type
            else:
                raise ValueError(f"type mismatch between {lhs} and {rhs} in {ex}")

            name = "%"+self.e.getName()
            if ex.op == "+":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fadd {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = add {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with + in {ex}")
                return Value(name, ty,"unnamed")
            elif ex.op == "-":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fsub {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = sub {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with - in {ex}")
                return Value(name, ty,"unnamed")
            elif ex.op == "*":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fmul {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = mul {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with * in {ex}")
                return Value(name, ty,"unnamed")
            #no unsigned types for the time being
            elif ex.op == "/":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fdiv {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = sdiv {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with / in {ex}")
                return Value(name, ty,"unnamed")
            elif ex.op == "%":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = frem {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = srem {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with % in {ex}")
                return Value(name, ty,"unnamed")
            elif ex.op == "==":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp oeq {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp eq {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
                return Value(name,"i1", "unnamed")
            elif ex.op == "!=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp one {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp ne {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
                return Value(name,"i1", "unnamed")
            elif ex.op == "<":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp olt {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp slt {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with < in {ex}")
                return Value(name,"i1", "unnamed")
            elif ex.op == "<=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp ole {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sle {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with <= in {ex}")
                return Value(name,"i1", "unnamed")
            elif ex.op == ">":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp ogt {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sgt {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with > in {ex}")
                return Value(name,"i1", "unnamed")
            elif ex.op == ">=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp oge {ty} {lhs.val}, {rhs.val}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sge {ty} {lhs.val}, {rhs.val}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with >= in {ex}")
                return Value(name,"i1", "unnamed")

            else:
                raise ValueError(f"unrecognized operation {ex.op} in {ex}")

        else:
            raise ValueError(f"{ex} isn't an expr dummy!")

    #TODO: expand from base types (pointers,arrays)
    #takes in a value, and then returns if that value can be converted to the given type without a cast
    def canConvert(self,value,typeTo):
        if value.isLit:
            if value.type[0] == 'i':
                return typeTo[0] == 'i'
            elif value.type == "double":
                return typeTo == "float" or typeTo == "double"
        #in theory
        else:
            return value.type == typeTo
    def close(self):
        self.e.close()
