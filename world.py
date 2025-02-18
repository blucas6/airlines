class Map:
    def __init__(self):
        self.offc = 40
        self.offr = 1
        self.main = []
        self.maxrow = 0
        self.maxcol = 0
        self.reset()

    def reset(self):
        with open("world.txt", "r") as f:
            tmp = f.readlines()
            for line in tmp:
                if line[0] != "#":
                    build_line = ""
                    for ch in line:
                        if ch != "\n":
                            build_line += ch
                    self.main.append(build_line)
        if self.main:
            self.maxcol = len(self.main[0])
            self.maxrow = len(self.main)
    
    def rowToMap(self, row):
        return row % self.maxrow

    def colToMap(self, col):
        return col % self.maxcol