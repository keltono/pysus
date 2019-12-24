class Token:
    def __init__(self, type, val=None, line=1): #TODO actually use line
        self.type = type #this would be a string
        self.val = val
        self.line = line
    def get_type(self): #ident, decimal, int, def, type(i.e int, which would be stored in val),
        return self.type
    def get_val(self):
        return self.val
    def get_lineno(self):
        return self.line
    def has_val(self): #might want it. who knows.
        True if self.val else False
    #don't see the need for setters
    def __str__(self):
        return "(type: '{}'  val: '{}')".format(self.type, self.val)
    def __repr__(self):
        return "(type: '{}'  val: '{}')".format(self.type, self.val)




