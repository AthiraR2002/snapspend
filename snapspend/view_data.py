import sqlite3
conn=sqlite3.connect("snapspend.db")
cursor=conn.cursor()
cursor.execute("SELECT * FROM expenses")
rows=cursor.fetchall()
print(rows)
conn.close()