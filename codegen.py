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

        self.e.addGlobal(d.name,d.name,self.e.typeToLLType(d.type))
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
        self.e.setIndent(0)
        self.codegenStatementList(d.body)
        self.e.scopeDown()
        print(self.e.currentScope.name)
        self.e.emmit("}")

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
            funcReturnType = self.e.getLLVarType("@"+self.e.currentScope.name[1])[1] #self.e.currentScope.name[0] is the file name
            #check and see if it incorrectly assumed literal type based on function return type, and readjust if needed
            #this will probably need to be reworked given oop
            if type(expr) == float:
                if funcReturnType == "double":
                    returnType = "double"
                elif funcReturnType == "float":
                    returnType = "float"
                else:
                    #if it's returning, we can probably assume that it would have been a parse error if it *wasn't* in a function
                    raise ValueError(f"return type mismatch in function {self.e.currentScope.name}: expected a(n) {funcReturnType}, saw a float")
            elif type(expr) == int:
                if funcReturnType == "i64" or funcReturnType == "i32" or funcReturnType == "i16" or funcReturnType == "i8":
                    returnType = funcReturnType
                else:
                    raise ValueError(f"return type mismatch in function {self.e.currentScope.name}: expected a(n) {funcReturnType}, saw an int")
            elif type(expr) == bool:
                returnType = "i1"
            else:
                returnType = self.e.getLocalVarType(expr)

            self.e.emmit(f"ret {returnType} {expr}")

    #GOD I LOVE PATTERN MATCHING
    #how this works is that it emmits any/all lines needed for the expr, and then returns a
    #string containing the SSA variable or the expected literal depending on the expr
    def codegenExpr(self, ex):
        #i'm dumb. not sure how to differentiate different sized literals
        #like, when is 4.0 a float and when is 4.0 a double? it depends on the context...
        t = type(ex)
        if t == ast.Literal:
            #TODO string and char literals
            if ex.val == True:
                return 1
            elif ex.val == False:
                return 0
            else:
                return str(ex.val)
        # if t == ast.
        else:
            raise ValueError(f"{ex} isn't an expr dummy!")


    def close(self):
        self.e.close()
