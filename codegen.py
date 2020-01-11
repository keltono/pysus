#this file handles the actual creation of IR based on input, emmiter.py handles the logic of emmiting IR
#i.e emmiter.py replaces the llvm library, and codegen.py does what it says on the tin
#well, kind of. codegen.py handles a lot of what the llvm library handles, emmiter.py really just handles the admin that comes with complex programs#the actual logic for deciding what line to write is here.

import ast
import emmiter

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
        self.e.scopeUp(d.name)
        self.e.setIndent(-1)

        self.e.addGlobal(d.name,"@"+d.name,self.e.typeToLLType(d.type))
        defline = f"define {self.e.typeToLLType(d.type[1][1])} @{d.name}("
        #args are stored as tuples in the form (type,name)
        #where type is a tuple of ("typeName",info)
        #(covered more in depth in emmiter.py)
        if d.args != []:
            llname = self.e.getName()
            lltype = self.e.typeToLLType(d.args[0][0])
            self.e.addVariable(d.args[0][1], llname, lltype)
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
        print(self.e.currentScope.name)
        self.e.emmit("}\n")

    def codegenStatementList(self, l):
        if l == None:
            pass
        else:
            for statement in l:
                self.codegenStatement(statement)
    #doesn't return anything, unlike the codegenExpr
    def codegenStatement(self, s):
        ty = type(s)
        if ty == ast.Return:
            expr = self.codegenExpr(s.returning)

            funcReturnType = self.e.getCurrFuncType()
            #check and see if it incorrectly assumed literal type based on function return type, and readjust if needed
            #this will probably need to be reworked given oop
            #in order to deal with the weak type system, SSA variables returned from codegen are 2-tuples of the form ("%name", "lltype")
            #bit of a hack, but eh. if it's stupid and it works...
            if self.canConvert(expr[1], funcReturnType):
                self.e.emmit(f"ret {funcReturnType} {expr[0]}")
            else:
                raise ValueError(f"return type mismatch in function {self.e.currentScope.name}: expected a(n) {funcReturnType}, saw {expr}")
            #the way I'm doing this right now will basically require me to have a special case for literals *anytime* i use a function

        #lets are scoped to the current function (or the global scope) like var declarations
        #doesn't actually generate any code past the code needed to evaluate the expression,
        #just adds it to the scope so that that value goes in wherever the variable is mentioned
        elif ty == ast.Let:
            expr = self.codegenExpr(s.val)
            if s.type == None:
                if expr[1] == "floating":
                    ty = "double"
                elif expr[1] == "int":
                    ty = "i32"
                elif expr[1] == "bool":
                    ty = "i1"
                else:
                    ty = expr[1]
            else:
                letLLType = self.e.typeToLLType(s.type)
                if self.canConvert(expr[1],letLLType):
                    ty = letLLType
                else:
                    #probably shouldn't emmit SSA values in error reporting...
                    raise ValueError(f"Expected a {letLLType} in let delcaration in function {self.e.currentScope.name[1]}, saw {expr}")
            print(expr[1])
            if expr[1] == "floating" or expr[1] == "int" or expr[1] == "bool":
                self.e.addVariable(s.name, expr[0], ty, isLit=True)
            else:
                self.e.addVariable(s.name, expr[0], ty)
        elif ty == ast.If:
            cond = self.codegenExpr(s.condition)
            if(cond[1][0] != "i" and cond[1] != "bool"):
                raise ValueError(f"expected boolean or integer in condition in if statement {s}, saw {cond}")

            if cond[1] == "bool":
                cmpType = "i1"
            elif cond[1] == "int":
               cmpType = "i32"
            else:
                cmpType = cond[1]

            cmpName = "%"+self.e.getName()
            thenName = self.e.getName()+"_then"
            failName = self.e.getName()+"_iffail"
            self.e.emmit(f"{cmpName} = icmp eq {cmpType} {cond[0]}, 1")
            self.e.emmit(f"br i1 {cmpName}, label %{thenName}, label %{failName}")
            self.e.emmitLabel(thenName)

            scopeName = self.e.getName()
            self.e.scopeUp(scopeName+"_then",increment=False)
            self.codegenStatementList(s.thenbody)
            self.e.scopeDown()

            #ifs, like C, unlike python, have their own scopes.
            if s.elsebody == None:
                self.e.emmit(f"br label {failName}")
                self.e.emmitLabel(failName)
            else:
                doneName = self.e.getName()+"_ifdone"
                self.e.emmit(f"br label {doneName}")
                self.e.emmitLabel(failName)
                self.e.scopeUp(scopeName+"_else", increment=False)
                self.codegenStatementList(s.elsebody)
                self.e.scopeDown()
                self.e.emmit(f"br label {doneName}")
                self.e.emmitLabel(doneName)

        else:
            self.codegenExpr(s)

    #how this works is that it emmits any/all lines needed for the expr, and then returns a
    # tuple of a string containing the SSA variable or the expected literal depending on the expr
    # and another string of their own type
    #int and floating are reserved for number literals and have special polymorphic properties (which sounds a lot fancier than it is)
    #bool isn't polymorphic, but it's useful to know when something is a literal
    #this whole literal system i've set up is way overly complex and kinda ruins the elegance of the program. Need to reconsider later.
    def codegenExpr(self, ex):
        t = type(ex)
        if t == ast.Literal:
            #TODO string and char literals
            if ex.val == True and type(ex.val) == bool:
                return ("1","bool")
            elif ex.val == False and type(ex.val) == bool:
                return ("0","bool")
            elif type(ex.val) == float:
                return (str(ex.val),"floating")
            elif type(ex.val) == int:
                return (str(ex.val), "int")
            else:
                raise ValueError(f"what the heck is this? I expected a literal of *some kind* but i saw {ex.val} in {ex}")
        #Variable reference, not a var declaration. returns ("llvm_name", "llvm_type")
        #e.g ("%1","i64")
        elif t == ast.Variable:
            return self.e.getLLVariable(ex.name)
        elif t == ast.Binary:
            #left recursion is fine here because eventually lhs won't be an binary expression
            lhs = self.codegenExpr(ex.lhs)
            rhs = self.codegenExpr(ex.rhs)

            if self.canConvert(lhs[1],rhs[1]):
                ty = rhs[1]
            elif self.canConvert(rhs[1], lhs[1]):
                ty = lhs[1]
            else:
                raise ValueError(f"type mismatch between {lhs} and {rhs} in {ex}")
            if ty == "int":
                ty = "i32"
            elif ty == "floating":
                ty = "double"
            elif ty == "bool":
                ty == "i1"

            name = "%"+self.e.getName()
            if ex.op == "+":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fadd {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = add {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with + in {ex}")
                return (name, ty)
            elif ex.op == "-":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fsub {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = sub {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with - in {ex}")
                return (name, ty)
            elif ex.op == "*":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fmul {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = mul {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with * in {ex}")
                return (name, ty)
            #no unsigned types for the time being
            elif ex.op == "/":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fdiv {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = sdiv {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with / in {ex}")
                return (name, ty)
            elif ex.op == "%":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = frem {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = srem {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with % in {ex}")
                return (name, ty)
            elif ex.op == "==":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp oeq {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp eq {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
                return (name, "i1")
            elif ex.op == "!=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp one {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp ne {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
                return (name, "i1")
            elif ex.op == "<":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp olt {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp slt {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with < in {ex}")
                return (name, "i1")
            elif ex.op == "<=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp ole {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sle {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with <= in {ex}")
                return (name, "i1")
            elif ex.op == ">":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp ogt {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sgt {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with > in {ex}")
                return (name, "i1")
            elif ex.op == ">=":
                if ty == "float" or ty == "double":
                    self.e.emmit(f"{name} = fcmp oge {ty} {lhs[0]}, {rhs[0]}")
                elif ty[0] == "i":
                    self.e.emmit(f"{name} = icmp sge {ty} {lhs[0]}, {rhs[0]}")
                else:
                    raise ValueError(f"Error: Type {ty} incompatable with >= in {ex}")
                return (name, "i1")

            else:
                raise ValueError(f"unrecognized operation {ex.op} in {ex}")

        else:
            raise ValueError(f"{ex} isn't an expr dummy!")

    #can I convert a variable to another type just by changing the type keyword?
    #used for literals, returns a bool
    #no implicit casts in my house!
    #not sure how to handle the mix of float literals where there should be an int and vice versa. I'm going to follow the rust model where
    #literals are given types, and any ad-hoc polymorphism must be handled by the individual function (so + will theoretically have casts built in)
    def canConvert(self,typeFrom,typeTo):
        if typeFrom == "int":
            return typeTo[0] == 'i' or typeTo== "int"
        elif typeFrom == "floating":
            return typeTo == "float" or typeTo == "double" or "floating"
        elif typeFrom == "bool":
            return typeTo[0] == "i" or typeTo == "bool"
        else:
            return typeFrom == typeTo


    def close(self):
        self.e.close()