import sqlite3

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