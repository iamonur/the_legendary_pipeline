import sqlite3
import os
import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

class DBWrapper:
    def __init__(self):
        self.dbname = randomword(16) + ".db"
        os.system("touch " + self.dbname)
        self.connection = sqlite3.connect(self.dbname)
        self.db = self.connection.cursor()
        self.init_table()

    def init_table(self):
        query = """ CREATE TABLE levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rng TEXT NOT NULL,
            rng_time REAL,
            mapgen_type TEXT NOT NULL,
            polish_type TEXT NOT NULL,
            spriter_type TEXT NOT NULL,
            mapgen_time REAL,
            model_time REAL,
            game_id INTEGER NOT NULL,
            sequence TEXT NOT NULL,
            ok_func_id INTEGER NOT NULL,
            isOK BOOLEAN NOT NULL
        );"""
        self.db.execute(query)

    def insertQ(self, line, linetime, ca, cap, sp, maptime, modeltime, game, seq, func_id, isOK):
        query = " INSERT INTO levels (rng,rng_time,mapgen_type,polish_type,spriter_type,mapgen_time,model_time,game_id,sequence,ok_func_id,isOK) values ('{}',{},'{}','{}','{}',{},{},{},'{}',{},{})".format(line,linetime,ca,cap,sp,maptime,modeltime,game,seq,func_id,isOK)
        print(query)
        self.db.execute(query)
        self.connection.commit()