from datetime import datetime

class timer:
    def __init__(self, goal = 0):
        self.last = datetime.now()
        self.goal = goal
    
    def reached(self):
        if self.timepassed() >= self.goal:
            return True
        return False

    def timepassed(self):
        return (datetime.now()-self.last).total_seconds()

    def reset(self):
        self.last = datetime.now()