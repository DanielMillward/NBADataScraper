class BaseDB():
    def __init__(self, keys=[], data=[]) -> None:
        self.keys = keys
        self.data = data

        self.add_to_db()

    def add_to_db(self):
        raise NotImplementedError("Base Class")
        #for page, pgdata in data:
		#- rows = turn_page_into_rows(page, pgdata)
		#- add_rows_to_db(rows)   

    def turn_pages_into_rows(self):
        raise NotImplementedError("Base Class")
    
    def add_rows_to_db(self):
        raise NotImplementedError("Base Class")