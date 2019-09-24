class Token:
    def __init__(self, type, value=None):
        self.type = type #this would be a string
        self.value = value
    def get_type(): #ident, decimal, int, def, type(i.e int, which would be stored in value),
        return self.type
    def get_value():
        return self.value
    def has_value(): #might want it. who knows.
        True if self.value else False
    #don't see the need for setters
    def __str__(self):
        return "(type: {}  value: {})".format(self.type, self.value)
    def __repr__(self):
        return "(type: {}  value: {})".format(self.type, self.value)




