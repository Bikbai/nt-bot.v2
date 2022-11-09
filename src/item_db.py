from datetime import datetime, timedelta
from time import time
from urllib import request

import jsonpickle

db_uri = 'https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/81018ce727f04f3fc3f41c1fdb5f6c7eeeeda912/items.json'
item_text_uri = 'https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/formatted/items.txt'
tmpfile = "tmp.json"

def test():
    #request.urlretrieve(db_uri, tmpfile)
    with open(tmpfile, "r") as file:
        s = file.read()
        if len(s) < 1:
            return True
        full_db = jsonpickle.decode(s)
        return full_db

x: dict[str, str] = test()
weapons = x.get('items').get('weapon')
for w in weapons:
    print(w)