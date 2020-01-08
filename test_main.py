import ast, codegen

a = ast.Def("cool", ("function", ([("int",None), ("double",None)], ("int",None))),[(("int",None),"wow"), (("double",None),"wow")], None)

c = codegen.Codegen("wow.ll")

c.codegenDef(a)

c.close()
