class fixedlist:
    def __init__(self, length):
        self.list = []
        self.length = length
        for i in range(length):
            self.list.append(None)
    
    def append(self, item):
        if len(self.list) >= self.length:
            del self.list[0]
            self.list.append(item)
    
    def getlast(self):
        return self.list[-1:][0]

    def getallvalues(self):
        l = []
        for i in self.list:
            if i:
                l.append(i)
        return l

    def string(self):
        out = "["+str(self.list[0])
        for i in self.list[1:]:
            out += ", "+str(i)
        out += "]"
        return out