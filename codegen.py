#this file handles the actual creation of IR based on input, emiter.py handles the logic of emiting IR
#i.e emiter.py replaces the llvm library, and codegen.py does what it says on the tin
#well, kind of. codegen.py handles a lot of what the llvm library handles, emiter.py really just handles the admin that comes with complex programs
#the actual logic for deciding what line to write is here.
#this could probably benefit from a sperate semantic analysis phase...
#TODO currently, all acorss the file everything is aligned to 1. this may cause issues with trampolines, and definitelly is not effecient enough
#I'm not really sure what it should be set to under x86-64 (or x86 for that matter) but, juding from clang, it's probably either 4 or 8 without fail.
#not brave enough for that right now, and it should work for everything (except, again, possibly trampolines)

import ast
import emiter
from value import Value

codegen_later = []

class Codegen:
    def __init__(self,fd,ast):
        #the emiter object. This is used a lot and therefore is shortened down
        self.e = emiter.Emiter(fd)
        self.ast = ast
        self.todos = []

    def codegen(self):
        for astNode in self.ast:
            t = type(astNode)
            if t == ast.Def:
                self.codegenDef(astNode)
            else:
               #only defs at the top level for now. I'll probably allow global variables at some point.
               raise ValueError(f"Expected a function defintion on the top level, saw {astNode}")
        self.e.emit_to_top_of_file(codegen_later,".ll") #need to make this extension stuff not bad at some point
        self.e.close()
        
        

    #takes in an ast.Def object, emits, returns nothing
    def codegenDef(self,d):
        #TODO support nested functions. they'll have to be generated outside of the function somehow
        #not totally sure how to handle that given the recusive-desent-esq control flow.
        #probably just something like a list of things that need to be genrated next, that's referenced after a function is generated.
        self.e.scopeUp(d.name, isFunction = True)
        self.e.setIndent(-1)

        self.e.addGlobal(d.name,"@"+d.name,self.e.typeToLLType(d.type), "function", False)

        returnType = self.e.typeToLLType(d.type[1][1])

        defline = f"define {returnType} @{d.name}("
        #args are stored as tuples in the form (type,name)
        #where type is a tuple of ("typeName",info)
        #(covered more in depth in emiter.py)
        if d.args != []:
            llname = "%"+self.e.getName()
            lltype = self.e.typeToLLType(d.args[0][0])
            self.e.addVariable(d.args[0][1], llname, lltype, "arg", d.args[0][0])
            defline +=f"{lltype} {llname}"
            d.args = d.args[1:]
            for arg in d.args:
                llname = "%"+self.e.getName()
                lltype = self.e.typeToLLType(arg[0])
                self.e.addVariable(arg[1], llname, lltype, "arg", arg[0])
                defline +=f", {lltype} {llname}"
        defline +=") {"
        self.e.emit(defline)
        self.e.emitLabel(f"{self.e.getName()}_entry")
        self.e.setIndent(0)

        #TODO maybe make it be like unit in ocaml instead of "void"?
        if returnType != "void":
            returnValue = "%"+self.e.getName()+"_return"
            self.e.emit(f"{returnValue} = alloca {returnType} ")
            self.e.setReturnValue(returnValue)
            returnLabel = self.e.getName()+"_returnLabel"
            self.e.setFuncReturnLabel(returnLabel)

        self.codegenStatementList(d.body)
        if returnType != "void":
            self.e.emit(f"br label %{returnLabel}")
            self.e.emitLabel(returnLabel)
            retLoadName = "%"+self.e.getName()
            self.e.emit(f"{retLoadName} = load {returnType}, {returnType}* {returnValue}, align 1")
            self.e.emit(f"ret {returnType} {retLoadName}")
        self.e.setIndent(-1)
        self.e.emit("}\n")
        self.e.scopeDown()
        #this will need to be modified in the case of nested functions
        for line in self.todos:
            self.e.emit(line)
        self.todos = []

    def codegenStatementList(self, l):
        if l != None:
            for statement in l:
                s = self.codegenStatement(statement)
                if s == 'break':
                    break
    #doesn't return anything, unlike the codegenExpr
    def codegenStatement(self, s):
        ty = type(s)
        if ty == ast.Return:
            return self.codegenReturn(s)
        elif ty == ast.Let:
            return self.codegenLet(s)
        elif ty == ast.Assign:
            return self.codegenAssign(s)
        elif ty == ast.Var:
            return self.codegenVar(s)
        elif ty == ast.If:
            return self.codegenIf(s)
        elif ty == ast.While:
            return self.codegenWhile(s)
        else:
            return self.codegenExpr(s)

    #returns a tuple containing the value and the type of the expr
    #e.g ("%example_0x0", "i32")
    #or ("2,"int")
    def codegenExpr(self, ex):
        t = type(ex)
        if t == ast.Literal:
            return self.codegenLiteral(ex)
        #Variable reference, not a var declaration. returns a NamedValue object
        elif t == ast.Variable:
            return self.codegenVariable(ex)
        elif t == ast.Call:
            return self.codegenCall(ex)
        elif t == ast.Unary:
            return self.codegenUnary(ex)
        elif t == ast.Index:
            return self.codegenIndex(ex)
        elif t == ast.Binary:
            return self.codegenBinary(ex)
        else:
            raise ValueError(f"{ex} isn't an expr dummy!")

    def codegenVar(self,s):
        expr = self.codegenExpr(s.val)
        if s.type == None:
            ty = expr.lltype
            s.type = expr.type
        else:
            varLLType = self.e.typeToLLType(s.type)
            if self.canConvert(expr, varLLType):
                ty = varLLType
            else:
                print(f"exprType = '{expr.lltype}'")
                print(f"varLLtype = '{varLLType}'")
                raise ValueError(f"Expected a {varLLType} in var delcaration in {self.e.currentScope.name[1]}, saw {expr}")
        varName = "%"+self.e.getName()
        #TODO trampolines might require a spesific alignment (that isn't 1) idk.
        self.e.emit(f"{varName} = alloca {ty}, align 1")
        self.e.emit(f"store {ty} {expr.val}, {ty}* {varName}, align 1")
        self.e.addVariable(s.name, varName, ty+"*", "var", s.type, expr.isLit)

    def codegenAssign(self,s):
        lhs = self.codegenExpr(s.lhs).lvalue
        rhs = self.codegenExpr(s.rhs)
        while(s.derefs):
            nextTy = lhs.lltype[:-1]
            loadTmp = "%"+self.e.getName()
            self.e.emit(f"{loadTmp}= load {nextTy}, {lhs.lltype} {lhs.val}")
            lhs.lltype = nextTy
            lhs.val = loadTmp
            s.derefs -= 1
        if lhs.lltype[-1] != '*':
            raise ValueError(f"cannot store into a variable that has be dereferenced to base type {ty} in {s}")
        if lhs.category != "var":
            raise ValueError(f"can't re-assign non-var variables. {s}")
        if rhs.isLit:
            if (rhs.lltype =="i32" or rhs.lltype == "i1") and lhs.lltype[0] == "i":
                rhs.lltype = lhs.lltype[:-1]
            elif rhs.lltype == "double" and lhs.lltype == "float*":
                rhs.lltype = "float"
        if lhs.lltype != rhs.lltype +"*":
            raise ValueError(f"type mismatch in assignment {s} lhs: {lhs.lltype} rhs: {rhs.lltype}")
        self.e.emit(f"store {rhs.lltype} {rhs.val}, {lhs.lltype} {lhs.val}, align 1")

    #doesn't actually generate any code past the code needed to evaluate the expression,
    #just adds it to the scope so that that value goes in wherever the variable is mentioned
    def codegenLet(self, s):
            #I *could* make it so you can't re-let variables, but where's the fun in that?
            #TODO make these stored in memory like vars, but just have them be immutable.
            expr = self.codegenExpr(s.val)
            if s.type == None:
                ty = expr.lltype
                s.type = expr.type
            else:
                print(s.type)
                letLLType = self.e.typeToLLType(s.type)
                if self.canConvert(expr, letLLType):
                    ty = letLLType
                else:
                    raise ValueError(f"Expected a {varLLType} in var delcaration in {self.e.currentScope.name[1]}, saw {expr}")
            varName = "%"+self.e.getName()
            #TODO trampolines might require a spesific alignment (that isn't 1) idk.
            #TODO i guess alignment depends on the variable type (go figure.) (4 for ints, floats, 8 for long, doubles, pointers)
            self.e.emit(f"{varName} = alloca {ty}, align 1")
            self.e.emit(f"store {ty} {expr.val}, {ty}* {varName}, align 1")
            self.e.addVariable(s.name, expr.val, ty+"*", "let", expr.type, expr.isLit)

    def codegenReturn(self, s):
            expr = self.codegenExpr(s.returning)

            funcLLReturnType = self.e.getCurrFuncLLType()[1]
            returnValue = self.e.getReturnValue()

            #TODO returns in void functions jumping to the end
            if funcLLReturnType == "void":
                raise ValueError(f"return statement in function with 'void' return type {s} in function {self.e.getCurrFunc()}")
            if returnValue == None:
                raise ValueError(f"no returnValue in function {self.e.getCurrFunc()} for return statement {s}")

            self.e.setCurrReturnLabel()

            if self.canConvert(expr, funcLLReturnType):
                self.e.emit(f"store {funcLLReturnType} {expr.val}, {funcLLReturnType}* {returnValue}, align 1")
            else:
                raise ValueError(f"return type mismatch in function {self.e.currentScope.name}: expected a(n) {funcLLReturnType}, saw {expr}")

    def codegenIf(self, s):
        cond = self.codegenExpr(s.condition)
        if(cond.lltype[0] != "i"):
            raise ValueError(f"expected boolean or integer in condition in if statement {s}, saw {cond}")

        #TODO: might need to do some work here to allow pointers and such
        cmpName = "%"+self.e.getName()
        thenName = self.e.getName()+"_then"
        failName = self.e.getName()+"_iffail"
        self.e.emit(f"{cmpName} = icmp ne {cond.lltype} {cond.val}, 0")
        self.e.emit(f"br i1 {cmpName}, label %{thenName}, label %{failName}")
        self.e.emitLabel(thenName)

        scopeName = self.e.getName()
        self.e.scopeUp(scopeName+"_then",False,increment=False)
        self.codegenStatementList(s.thenbody)
        doneName = self.e.getName()+"_ifdone"
        ifReturns = False

        if self.e.currHasReturnLabel():
            self.e.emit(f"br label %{self.e.getFuncReturnLabel()}")
            ifReturns = True
        elif s.elsebody == None:
            self.e.emit(f"br label %{failName}")
        else:
            self.e.emit(f"br label %{doneName}")

        self.e.emitLabel(failName)
        self.e.scopeDown()

        if s.elsebody == None:
            return

        self.e.scopeUp(scopeName+"_else",isFunction=False,increment=False)
        self.codegenStatementList(s.elsebody)

        if self.e.currHasReturnLabel():
            self.e.emit(f"br label %{self.e.getFuncReturnLabel()}")
            if ifReturns:
                return 'break'
        else:
            self.e.emit(f"br label %{doneName}")
        self.e.emitLabel(doneName)
        self.e.scopeDown()
    def codegenWhile(self, s):
        cond = self.codegenExpr(s.condition)
        if(cond.lltype[0] != "i"):
            raise ValueError(f"expected boolean or integer in condition in if statement {s}, saw {cond}")
        cmpName = "%"+self.e.getName()
        thenName = self.e.getName()+"_whileBody"
        failName = self.e.getName()+"_whileFail"
        self.e.emit(f"{cmpName} = icmp ne {cond.lltype} {cond.val}, 0")
        self.e.emit(f"br i1 {cmpName}, label %{thenName}, label %{failName}")
        self.e.emitLabel(thenName)

        bodyScopeName = self.e.getName()+"_while"
        self.e.scopeUp(bodyScopeName,False,increment=False)
        self.codegenStatementList(s.body)

        #always returns in this case, returns in if statement are handled there


        if self.e.currHasReturnLabel():
            self.e.emit(f"br label %{self.e.getFuncReturnLabel()}")
        else:
            insideCond = self.codegenExpr(s.condition)
            self.e.emit(f"{cmpName}_inside = icmp ne {insideCond.lltype} {insideCond.val}, 0")
            self.e.emit(f"br i1 {cmpName}_inside, label %{thenName}, label %{failName}")
        self.e.emitLabel(failName)
        self.e.scopeDown()

    def codgenCall(self,ex):
        argExprs = []
        for arg in ex.args:
            argExprs.append(self.codegenExpr(arg))
        try:
             func = self.e.getLLVariable(ex.name)
        except ValueError:
            raise ValueError(f"uknown function {ex.name} in function call")
        argStr = ""
        for index, arg in enumerate(argExprs):
            #func.type[0] is the arg types
            if arg.lltype != func.lltype[0][index]:
                if arg.isLit:
                    if not canConvert(arg,func.lltype[0][index]):
                        raise ValueError(f"type mismatch between argument {index + 1} {arg} and function {func} in call {s}: expected {func.lltype[0][index]}, saw {arg.lltype}")
                else:
                    raise ValueError(f"type mismatch between argument {index + 1} {arg} and function {func} in call {s}: expected {func.lltype[0][index]}, saw {arg.lltype}")
            if index == 0:
                argStr+= f"{arg.lltype} {arg.val}"
            else:
                argStr+= f",{arg.lltype} {arg.val}"

        llName = "%"+self.e.getName()
        self.e.emit(f"{llName} = call {func.lltype[1]} {func.val}({argStr})")
        return Value(llName, func.lltype[1], "unnamed", False)
    def codegenBinary(self, ex):
        #left recursion is fine here because eventually lhs won't be an binary expression
        lhs = self.codegenExpr(ex.lhs)
        rhs = self.codegenExpr(ex.rhs)

        #ocasionally dynamic typing is nice

        if lhs.type[0] == 'pointer' and rhs.type[0][0]=='i':
            ty = lhs.lltype
        #TODO add arrays here (should work the same as pointers)
        elif rhs.type[0] == 'pointer' and lhs.type[0][0]=='i':
            ty = rhs.lltype

        elif self.canConvert(lhs,rhs.lltype):
            ty = rhs.lltype
        elif self.canConvert(rhs, lhs.lltype):
            ty = lhs.lltype
        else:
            raise ValueError(f"type mismatch between {lhs} and {rhs} in {ex}")

        name = "%"+self.e.getName()
        if ex.op == "+":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fadd {ty} {lhs.val}, {rhs.val}")
            elif ty[-1] == '*':
                if rhs.type[0] == 'pointer':
                    self.e.emit(f"{name} = getelementptr {ty[:-1]}, {ty} {rhs.val}, {lhs.lltype} {lhs.val}")
                    return Value(name,ty, rhs.category, rhs.type)
                elif lhs.type[0] == 'pointer':
                    self.e.emit(f"{name} = getelementptr {ty[:-1]}, {ty} {lhs.val}, {rhs.lltype} {rhs.val}")
                    return Value(name,ty, lhs.category, lhs.type)
                else:
                    raise ValueError(f"need a pointer to do pointer math, dummy, in {ex}")
            elif rhs.type[0] == "pointer" or lhs.type[0] == "pointer":
                raise ValueError(f" not sure how you have a pointer type without a * in the lltype {ty} in {ex}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = add {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with + in {ex}")
            return Value(name, ty, "unnamed", lhs.type)
        elif ex.op == "-":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fsub {ty} {lhs.val}, {rhs.val}")
            elif ty[-1] == '*':
                subName = "%"+self.e.getName()
                if rhs.type[0] == 'pointer':
                    self.e.emit(f"{subName} = sub {lhs.lltype} 0, {lhs.val}")
                    self.e.emit(f"{name} = getelementptr {ty[:-1]}, {ty} {rhs.val}, {lhs.lltype} {subName}")
                    return Value(name,ty, rhs.category, rhs.type)
                elif lhs.type[0] == 'pointer':
                    self.e.emit(f"{subName} = sub {rhs.lltype} 0, {rhs.val}")
                    self.e.emit(f"{name} = getelementptr {ty[:-1]}, {ty} {lhs.val}, {rhs.lltype} {subName}")
                    return Value(name,ty, lhs.category, lhs.type)
                else:
                    raise ValueError(f"need a pointer to do pointer math, dummy, in {ex}")
            elif rhs.type[0] == "pointer" or lhs.type[0] == "pointer":
                raise ValueError(f" not sure how you have a pointer type without a * in the lltype {ty} in {ex}")

            elif ty[0] == "i":
                self.e.emit(f"{name} = sub {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with - in {ex}")
            return Value(name, ty, "unnamed",lhs.type)
        elif ex.op == "*":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fmul {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = mul {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with * in {ex}")
            return Value(name, ty, "unnamed",lhs.type)
        #no unsigned types for the time being
        elif ex.op == "/":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fdiv {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = sdiv {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with / in {ex}")
            return Value(name, ty, "unnamed",lhs.type)
        elif ex.op == "%":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = frem {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = srem {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with % in {ex}")
            return Value(name, ty, "unnamed",lhs.type)
        elif ex.op == "==":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp oeq {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp eq {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
            return Value(name,"i1","unnamed",("bool",None))
        elif ex.op == "!=":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp one {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp ne {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with == in {ex}")
            return Value(name,"i1","unnamed",("bool",None))
        elif ex.op == "&&":
            lhsTempName = "%"+se.e.getName()
            rhsTempName = "%"+se.e.getName()
            #no real reason that each side couldn't be a different type
            #but also no real reason that you would want that i think
            self.e.emmit(f"{lhsTempName} == icmp ne {ty} {lhs.val} 0")
            self.e.emmit(f"{rhsTempName} == icmp ne {ty} {rhs.val} 0")
            self.e.emmit(f"{name} = and i1 {lhs.val}, {rhs.val}")
        elif ex.op == "||":
            lhsTempName = "%"+se.e.getName()
            rhsTempName = "%"+se.e.getName()
            #no real reason that each side couldn't be a different type
            #but also no real reason that you would want that i think
            self.e.emmit(f"{lhsTempName} == icmp ne {ty} {lhs.val} 0")
            self.e.emmit(f"{rhsTempName} == icmp ne {ty} {rhs.val} 0")
            self.e.emmit(f"{name} = or i1 {lhs.val}, {rhs.val}")

        elif ex.op == "<":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp olt {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp slt {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with < in {ex}")
            return Value(name,"i1","unnamed",("bool",None))
        elif ex.op == "<=":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp ole {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp sle {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with <= in {ex}")
            return Value(name,"i1","unnamed",("bool",None))
        elif ex.op == ">":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp ogt {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp sgt {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with > in {ex}")
            return Value(name,"i1","unnamed",("bool",None))
        elif ex.op == ">=":
            if ty == "float" or ty == "double":
                self.e.emit(f"{name} = fcmp oge {ty} {lhs.val}, {rhs.val}")
            elif ty[0] == "i":
                self.e.emit(f"{name} = icmp sge {ty} {lhs.val}, {rhs.val}")
            else:
                raise ValueError(f"Error: Type {ty} incompatable with >= in {ex}")
            return Value(name,"i1","unnamed",("bool",None))

        else:
            raise ValueError(f"unrecognized operation {ex.op} in {ex}")

    def codegenLiteral(self, ex):
        print(ex)
        if ex.val == True and type(ex.val) == bool:
            return Value("1","i1","unnamed",("bool",None),True)
        elif ex.val == False and type(ex.val) == bool:
            return Value("0","i1","unnamed", ("bool", None), True)
        elif type(ex.val) == float:
            return Value(str(ex.val),"double", "unnamed", ("double",None), True)
        elif type(ex.val) == int:
            return Value(str(ex.val), "i32", "unnamed", ("int",None), True)
        elif type(ex.val) == str and len(ex.val) == 1:
            return Value(ord(ex.val), "i8", "unnamed", ("char",None), True)
        elif type(ex.val) == str: #this is so dumb. I'll keep it for now, but this is just really stupid
            arrayLen = len(ex.val)+1
            arrayPtr = "%"+self.e.getName()
            arrayType = f"[{arrayLen} x i8]"
            self.e.emit(f"{arrayPtr} = alloca {arrayType}, align 1")

            ptrPtr = "%"+self.e.getName()
            self.e.emit(f"{ptrPtr} = bitcast {arrayType}* {arrayPtr} to i8*")
            self.e.emit(f"call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 {ptrPtr}, i8* align 1 getelementptr inbounds ({arrayType}, {arrayType}* @__const.main.{ptrPtr[1:]}, i32 0, i32 0), i64 {arrayLen}, i1 false)")
            codegen_later.append( f"@__const.main.{ptrPtr[1:]} = private unnamed_addr constant {arrayType} c\"{ex.val}\\00\", align 1 " )
            if "declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)" not in codegen_later:
                codegen_later.append("declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)")

            return Value(arrayPtr, arrayType+"*", "unnamed", ("array", (arrayLen, ("char",None))), True)
            

        #NOTE due to reasons, array literals are stored in memory before being served
        #What this does is allocate the correct size of memory, does n many GEP instructions and stores the correct values in each of those pointers
        #eventually returns a pointer of the base type (e.g [3 x i32] -> i32*)
        elif type(ex.val) == list: #FIXME wow this is bad
            exprList = []
            for expr in ex.val:
                exprList.append(self.codegenExpr(expr))
            for expr in exprList:
                if expr.type != exprList[0].type:
                    raise ValueError(f"Value mismatch between terms in array literal. Saw {expr.type}, expected {exprList[0].type}")

            arrayPtr = "%"+self.e.getName()
            arrayType = f"[{len(exprList)} x {exprList[0].lltype}]"

            self.e.emit(f"{arrayPtr} = alloca {arrayType}, align 4")

            gepName = "%"+self.e.getName()
            elemType = exprList[0].lltype
            self.e.emit(f"{gepName}_arr_init = getelementptr {arrayType}, {arrayType}* {arrayPtr}, i64 0, i64 0 ")
            self.e.emit(f"store {elemType} {exprList[0].val}, {elemType}* {gepName}_arr_init, align 1")
            exprList = exprList[1:]
            for index, expr in enumerate(exprList):
                self.e.emit(f"{gepName}_arr_{index} = getelementptr {elemType}, {elemType}* {gepName}_arr_init, i64 {index+1}")
                self.e.emit(f"store {elemType} {exprList[index].val}, {elemType}* {gepName}_arr_{index}, align 1")
            return Value(arrayPtr, arrayType+"*", "unnamed", ("array", (len(exprList)+1, exprList[0].type)), True)
        # elif 
        else:
            raise ValueError(f"what the heck is this? I expected a literal of *some kind* but i saw {ex.val} in {ex}")

    def codegenVariable(self,ex):
        var = self.e.getLLVariable(ex.name)
        if var.category == "arg":
            return var
        elif var.category == "var" or var.category == 'let':
            loadName = "%"+self.e.getName()
            #take off a pointer level
            loadType = var.lltype[:-1]
            self.e.emit(f"{loadName} = load {loadType}, {var.lltype} {var.val}, align 1")
            #TODO see if calling both the var pointer and the var result "var" causes issues
            return Value(loadName, loadType, var.category, var.type, False, lvalue=var)
        else:
            raise ValueError(f"uknown category {var.category}")

    def codegenIndex(self, ex):
        arr = self.codegenExpr(ex.op)
        print(ex)
        print(arr)
        print(arr.type)
        print(arr.type[1])
        if arr.type[0] != 'array':
            raise ValueError(f"no indexing non-array variables in {ex}")
        indexName = "%"+self.e.getName()
        #arrays types generally corrospond to array ptrs in llvm
        #actually will get  a element_type* which can be stored in directly
        ptrType = arr.lltype
        arrType = arr.lltype[:-1]
        #should be elem type...
        elemType = self.e.typeToLLType(arr.type[1][1])
        elemTypePtr = elemType+"*"
        self.e.emit(f"{indexName} = getelementptr {arrType}, {ptrType} {arr.val}, i64 0, i64 {ex.index.val}")

        loadName = "%"+self.e.getName()

        #TODO meaningful alignment
        self.e.emit(f"{loadName} = load {elemType}, {elemTypePtr} {indexName}, align 1")

        #FIXME idk if cateogry is *actually* maintained
        return Value(loadName, elemType, arr.category, arr.type[1][1],lvalue = Value(indexName, elemTypePtr, arr.category, arr.type[1][1], False))
    def codegenUnary(self, ex):
        unaryName = "%"+self.e.getName()
        if ex.op == '-' or ex.op == '!' or ex.op =='*':
            operand = self.codegenExpr(ex.operand)

            if ex.op == "-":
                if operand.lltype == "double" or operand.lltype == "float":
                    self.e.emit(f"{unaryName} = fsub {operand.lltype} 0.0, {operand.val}")
                elif operand.lltype[0] == "i":
                    self.e.emit(f"{unaryName} = sub {operand.lltype} 0, {operand.val}")
                else:
                    raise ValueError(f"invalid type {ex.lltype} for - unary operator in {ex}")
                return Value(unaryName, operand.lltype,"unnamed",operand.type, False)
            elif ex.op == "!":
                if operand.lltype == "double" or operand.lltype == "float":
                    self.e.emit(f"{unaryName} = fcmp oeq {operand.lltype} 0.0, {operand.val}")
                elif operand.lltype[0] == "i":
                    self.e.emit(f"{unaryName} = icmp eq {operand.lltype} 0, {operand.val}")
                else:
                    raise ValueError(f"invalid type {operand.lltype} for ! unary operator in {ex}")
                return Value(unaryName, "i1", "unnamed",operand.type, False)
            elif ex.op == "*":
                if operand.type[0] != "pointer":
                    raise ValueError(f"no dereferencing non-pointer types in {ex}")
                loadType = operand.lltype[:-1]
                self.e.emit(f"{unaryName} = load {loadType}, {operand.lltype} {operand.val}, align 1")
                return Value(unaryName, loadType, operand.category, operand.type[1], False, lvalue=operand)

        if ex.op == '&':
            #only works on named values, unlike deref
            #TODO it should probably be able to work on a unary of a deref (if not a unary of a ref)
            operand = self.e.getLLVariable(ex.operand.name)
            if operand.lltype [-1] != "*":
                raise ValueError(f"no referencing unnamed values in {ex}")
            #this idea of just returning what they are in memory to things that aren't pointer might have to change given arrays
            #so, normally, when a variable is referenced, it does a load.
            #the idea here, is that if the operand isn't a pointer, just don't do that, and it is effectivly a pointer level up
            #this works in all cases where the thing expected is the load value.
            #if something is expecting the additional pointer, then that needs to be taken into account

            if operand.type[0] != "pointer" and operand.lltype[-1] == '*':
                return Value(operand.val, operand.lltype, operand.category, ("pointer", operand.type), False)

            refType = operand.lltype+'*'
            self.e.emit(f"{unaryName} = alloca {operand.lltype}, align 1")
            self.e.emit(f"store {operand.lltype} {operand.val}, {refType} {unaryName}, align 1")

    #TODO: expand from base types (pointers,arrays)
    #takes in a value, and then returns if that value can be converted to the given type without a cast
    def canConvert(self,value,typeTo):
        if value.isLit:
            if value.lltype[0] == 'i':
                return typeTo[0] == 'i'
            elif value.lltype == "double":
                return typeTo == "float" or typeTo == "double"
            else:
                return value.lltype == typeTo
        #in theory
        else:
            return value.lltype == typeTo
