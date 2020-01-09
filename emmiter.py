#Note: this file has a lot of comments. this is partially good for understanding, but it's kind of rambly I used the comments to replace my whiteboard a good chunk of the time.
#TODO: handle scope switching (up and down in and out of functions)
#TODO: handle tags (probably just need something like a list of tags and line numbers in the scope, and a current tag var (all of which with line no.s)
#TODO: actually emmiting to a file
#TODO: write helper methods to emit spesific commands

#handles llvm contexts, states, scopes, oh my!
class Emmiter:

        #class that manages handling of scope. general idea is that it functions as a wrapper around a dictionary for the most part,
        #unless it cannot find a symbol in the dictionary, in which case it goes to a "higher level scope" (e.g the global scope if the current scope is a function scope)
    class Scope:
        def __init__(self,name,parent,indent):
            #a dictionary containing all named values in the scope, in the form of
            #name : ('llvm_var_name','llvm_type')
            #for now all functions are added to the global scope, but that's most likely due to change.
            #functions are stored as a tuple of a list of arg types and a return type
            #e.g ("@functionName", (["i64","i32"],"double"))
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

            #literally what it says on the tin. how many times it should indent when emmiting.
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
        def addNamedValue(self,name,llvar,lltype):
            self.namedValues[name] = (llvar, lltype)
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


        self.globalScope = self.Scope((self.outFile,"global"),None,-1)

        self.currentScope = self.globalScope


        self.emmit(f"; ModuleID = '{outFile}'\n")

        #TODO: handle typedefs & structs. maybe move this to the scope later?
        self.baseTypes =  {
            "int" : "i32",
            "long" : "i64",
            "float" : "float",
            "double" : "double",
            "bool" : "i1",
            "char" : "i8"
        }

        #TODO emmit module name & other metadata

    #adds a variable to the current scope. in theory, the llname will be provided by the previous step in codegen.
    #also adds it to the "llVar" list
    def addVariable(self,name, llname, lltype, isLit=False):
        self.currentScope.namedValues[name] = (llname, lltype)
        if not isLit:
            self.llVars[llname] = lltype
    def addGlobal(self, name, llname, lltype, isLit=False):
        self.currentScope.namedValues[name] = (llname, lltype)
        if not isLit:
            self.llVars[llname] = lltype

    #returns the llvm variable name given the "proper" variable name and type
    #e.g "foo" -> ("%example_2", "i32")
    #the way i'm storing vars has a lot of redundency... probably not good.
    def getLLVariable(self,var):
        return self.currentScope.getNamedValue(var)
    #returns the llvm variable type given the llvm variable name
    #e.g "%example_2" -> "i64"
    #only works on variables not defined by a literal, and thus should be used sparingly
    def getLLVarType(self,var):
        try:
            return self.llVars[var]
        except KeyError:
            print(self.llVars)
            raise KeyError(f"Uknown variable or function {var}")

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
    def scopeUp(self, name):
        newScope = self.Scope((self.outFile, name), self.currentScope,self.currentScope.indent + 1)
        self.currentScope = newScope

    def scopeDown(self):
        self.currentScope = self.currentScope.parent

    def setIndent(self,ind):
        self.currentScope.updateIndent(ind)

    def emmit(self, output):
        self.fd.write(self.currentScope.indentStr+output+"\n")

    def close(self):
        self.fd.close()
