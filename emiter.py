from value import Value
#Note: this file has a lot of comments. this is partially good for understanding, but it's kind of rambly.
#handles llvm contexts, states, scopes, oh my!
class Emiter:
        #class that manages handling of scope. general idea is that it functions as a wrapper around a dictionary for the most part,
        #unless it cannot find a symbol in the dictionary, in which case it goes to a "higher level scope" (e.g the global scope if the current scope is a function scope)
    class Scope:
        def __init__(self,name,parent,isFunction, indent):
            #a dictionary containing all named values in the scope, in the form of
            #name : ('llvm_var_name','llvm_type')
            #for now all functions are added to the global scope.
            #functions are stored as a Value objects
            self.namedValues = {}
            #tuple of the filename and function name or "global"
            #e.g ("example", "global")
            #will have to expand this if/when adding classes.
            self.name = name
            #the greater scope. theoretically, all thats in a function's scope is what's defined in those functions
            #the program would have to refrence back to the "parent scope" to get things defined outside the function
            #(for now the parent scope of a function is always a global, but that's due to change)
            #parent is None for the global scope
            self.parent = parent

            self.retLabel = None

            if parent == None:
                self.retValue = None
            else:
                self.retValue = parent.retValue

            # self.isFunction = isFunction

            #literally what it says on the tin. how many times it should indent when emiting.
            self.indent = indent

            self.indentStr = ""

            self.updateIndent(indent)

        def updateIndent(self, i):
            self.indent = i
            c = 0
            self.indentStr= ""
            while c <= i:
                self.indentStr += "\t"
                c+=1

        #these do as it says on the tin, as described above
        def addNamedValue(self,name,llvar,lltype,category, type, isLit=False):
            self.namedValues[name] = Value(llvar,lltype,category, type, isLit)
        def getNamedValue(self,name):
            try:
                return self.namedValues[name]
            except:
                if self.parent == None:
                    raise ValueError(f"unknown named value {name}")
                return self.parent.getNamedValue(name)

    def __init__(self, outFile):
        #number of local variable names
        #if only using numbers as variable names is good enough for llvm, its good enough for me!
        #written out as hex in the file
        self.names = 0

        #the name of the current file, used for scoping
        #kinda lazy and assumes ".ll" ending, but I don't really see a case where that should come up
        self.outFile = outFile[:3]

        #actual file object that is written to
        self.fd = open(outFile,"w+")

        #local variables dictionary. stores them in the form "name" : "lltype"
        #e.g "%filename_1" : "i64"
        self.llVars = {}


        self.globalScope = self.Scope((self.outFile,"global"),None,False,-1)

        self.currentScope = self.globalScope


        self.emit(f"; ModuleID = '{outFile}'\n")

        #TODO: handle typedefs & structs. maybe move this to the scope later?
        self.baseTypes =  {
            "int" : "i32",
            "long" : "i64",
            "float" : "float",
            "floating": "double",
            "double" : "double",
            "bool" : "i1",
            "char" : "i8"
        }

        #TODO emit module name & other metadata

    #adds a variable to the current scope. in theory, the llname will be provided by the previous step in codegen.
    #also adds it to the "llVar" list
    def addVariable(self,name, llname, lltype, category, type, isLit=False):
        self.currentScope.addNamedValue(name, llname, lltype, category, type, isLit)
        if not isLit:
            self.llVars[llname] = lltype
    def addGlobal(self, name, llname, lltype, category, type, isLit=False):
        self.globalScope.addNamedValue(name, llname, lltype, category, type, isLit)
        if not isLit:
            self.llVars[llname] = lltype

    #returns the llvm variable name given the "proper" variable name and type
    #e.g "foo" -> NamedValue("%example_0x2", "i32", "var", False)
    def getLLVariable(self,var):
        return self.currentScope.getNamedValue(var)
    #returns the llvm variable type given the llvm variable name
    #e.g "%example_2" -> "i64"
    #only works on variables not defined by a literal, and thus should be used sparingly
    def getLLVarType(self,var):
        try:
            return self.llVars[var]
        except KeyError:
            raise KeyError(f"Uknown variable or function {var}")

    def getCurrFuncLLType(self):
        return self.getCurrFunc().lltype

    def getCurrFunc(self):
        scopeTmp = self.currentScope
        while scopeTmp.parent != None:
            try:
                return self.currentScope.getNamedValue(scopeTmp.name[1])
            except:
                scopeTmp = scopeTmp.parent
        raise ValueError("Error: no function in scope!")
    def getFuncReturnLabel(self):
        return self.getCurrFunc().retLabel

    def setFuncReturnLabel(self, returnName):
        #not sure if this would work... I think it will because, iirc, python variables are all pointers which are passeds by value
        self.getCurrFunc().retLabel = returnName

    def currHasReturnLabel(self):
        return self.currentScope.retLabel != None

    #sets it to the same return as the function
    def setCurrReturnLabel(self):
        self.currentScope.retLabel = self.getCurrFunc().retLabel

    def setReturnValue(self, value):
        self.getCurrFunc().retValue = value

    def getReturnValue(self):
        return self.getCurrFunc().retValue

    def getName(self):
        name = self.outFile+ "_"+hex(self.names)
        self.names +=1
        return name

    #I just remembered how hard this is
    #(like, with pointers and arrays)
    #here's the plan: represent type like this:
    # (typename, info)
    #e.g ("int", None)
    #or ("array", (4, ("int", None)))
    #or ("pointer", ("array", (4, ("array", (5, ("int",None))))))
    #or ("function",([("int",None),("int",None)],("int", None)))
    def typeToLLType(self, ty):
        try:
            return self.baseTypes[ty[0]]
        except:
            #semi-related: I'm going to have to think long and hard how to handle arrays at any sort of hight level
            #(e.g directly returnable by a function)
            if ty[0] == "array":
                return f"[{(ty[1][0])} x {self.typeToLLType(ty[1][1])}]"
            elif ty[0] == "pointer":
                return self.typeToLLType(ty[1]) + "*"
            elif ty[0] == "function":
                #just return the return type
                argTypes = []
                for arg in ty[1][0]:
                    argTypes.append(self.typeToLLType(arg))
                return (argTypes, self.typeToLLType(ty[1][1]))
            else:
                #TODO line reporting error handling
                #maybe develop a proper stack trace error reporting system?
                raise ValueError(f"unknown type {ty[0]}")
    def scopeUp(self, name, isFunction,increment = True):
        if increment:
            i = 1
        else:
            i = 0
        newScope = self.Scope((self.outFile, name), self.currentScope, isFunction, self.currentScope.indent + i)
        self.currentScope = newScope

    def scopeDown(self):
        self.currentScope = self.currentScope.parent

    def setIndent(self,ind):
        self.currentScope.updateIndent(ind)

    def emit(self, output):
        self.fd.write(self.currentScope.indentStr+output+"\n")

    def emitLabel(self, label):
        self.fd.write(label+":\n")

    def close(self):
        self.fd.close()
