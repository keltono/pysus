#a struct containing the information for any value used in the codegen phase
#so far: let variables, literals, var variables, functions
class Value:
    #where category is ("function","var","let", "unnamed"). can't think of a better name.
    #type here is the llType
    def __init__(self, val, lltype, category, type,  isLit=False):
        self.type = type
        self.lltype = lltype
        self.val = val
        self.category = category
        self.isLit = isLit
    def __repr__(self):
        return f"Value(val: {self.val} lltype: {self.lltype} category: {self.category} type: {self.type} isLit: {self.isLit})"
    def __str__(self):
        return f"Value(val: {self.val} lltype: {self.lltype} category: {self.category} type: {self.type} isLit: {self.isLit})"
