from database import Database

class Xlsx2Db:
    def __init__(self):
        pass
    def xlsx2db(self, data):
        base = Database()
        for i in data:
            base.insert_xlsx(i[0],i[1])