class vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # change methods
    def move(self, pos):
        self.x += pos.x
        self.y += pos.y

    # return methods
    def string(self):
        return "("+str(self.x)+","+str(self.y)+")"

    def tuple(self):
        return (self.x, self.y)

    def equals(self, pos):
        if self.x == pos.x and self.y == pos.y:
            return True
        else:
            return False

    def plus(self, pos):
        return vector2(int(self.x + pos.x), int(self.y + pos.y))
    
    def minus(self, pos):
        return vector2(int(self.x - pos.x), int(self.y - pos.y))

    def times(self, pos):
        return vector2(int(self.x * pos.x), int(self.y * pos.y))

    def divided(self, pos):
        return vector2(int(self.x / pos.x), int(self.y / pos.y))
    
    def range(self, radius): # return a range (two positions) that has a certain radius
        return [vector2(self.x, self.y).minus(radius), vector2(self.x, self.y).plus(radius)]
    
    def insiderange(self, pos1, pos2):
        # psst, this method was made with ChatGPT ;)

        # Check if the position is already within the range
        if pos1.x <= self.x <= pos2.x and pos1.y <= self.y <= pos2.y:
            return vector2(self.x, self.y)

        # Calculate the nearest x-coordinate within the range
        if self.x < pos1.x:
            nearest_x = pos1.x
        elif self.x > pos2.x:
            nearest_x = pos2.x
        else:
            nearest_x = self.x

        # Calculate the nearest y-coordinate within the range
        if self.y < pos1.y:
            nearest_y = pos1.y
        elif self.y > pos2.y:
            nearest_y = pos2.y
        else:
            nearest_y = self.y

        return vector2(nearest_x, nearest_y)