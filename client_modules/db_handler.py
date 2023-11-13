import sqlite3
import os
import pickle

# for now, all the data lies in a single db file. this must be changed in the future.
initialize = """
CREATE TABLE IF NOT EXISTS users (
    UUID TEXT NOT NULL, 
    USERNAME TEXT UNIQUE NOT NULL, 
    FULL_NAME TEXT NOT NULL, 
    DOB TEXT NOT NULL, 
    EMAIL TEXT, 
    CREATION DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (UUID)
);
CREATE TABLE IF NOT EXISTS rooms (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    CREATOR_UUID TEXT NOT NULL, 
    ROOM_TYPE INTEGER NOT NULL, 
    MEMBERS BLOB NOT NULL, 
    CHAT_TABLE TEXT NOT NULL, 
    FOREIGN KEY(CREATOR_UUID) REFERENCES chatapp_accounts.users(UUID)
);
"""
createroom = """CREATE TABLE ? (
  messageID INTEGER PRIMARY KEY AUTOINCREMENT,
  messageUUID TEXT UNIQUE NOT NULL,
  sender TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  message BLOB NOT NULL,
  type TEXT NOT NULL,
  pinned INTEGER NOT NULL DEFAULT 0
);
"""

queries = {'initialize': initialize, 'create_room':createroom}
fields_to_check = {
    'username':{'table':'users','attribute':'USERNAME'},
    'room':{'table':'rooms', 'attribute':'CHAT_TABLE'}
    }

class db:
    con = None
    cur = None

def create_db(workingdir): # todo: add password protection
    conn = sqlite3.connect(f'{workingdir}/DATA.db')
    conn.close()
    
def decrypt_creds(fkey, workingdir):
    with open(f'{workingdir}/creds/db', 'rb') as f:
        data = f.read()
    decrypted = fkey.decrypt(data)
    dict = pickle.loads(decrypted)
    try:
        setattr(db, 'con', sqlite3.connect(dict['file']))
        setattr(db, 'cur', db.con.cursor())
        print('[INFO] Loaded Database')
    except Exception as e:
        print('[ERROR] Could not load database:', e)

# # Create a connection object with the database
# conn = sqlite3.connect('my_database.db')

# # Set password for the db file
# conn.execute("PRAGMA key='password'")

# # Create tables
# conn.execute('''CREATE TABLE IF NOT EXISTS table1 (column1 datatype PRIMARY KEY (one or more columns), column2 datatype, column3 datatype, ….. columnN datatype);''')
# conn.execute('''CREATE TABLE IF NOT EXISTS table2 (column1 datatype PRIMARY KEY (one or more columns), column2 datatype, column3 datatype, ….. columnN datatype);''')

# # Insert data into tables
# conn.execute("INSERT INTO table1 VALUES ('value1', 'value2', 'value3')")
# conn.execute("INSERT INTO table2 VALUES ('value4', 'value5', 'value6')")

# # Commit changes and close connection
# conn.commit()
# conn.close()