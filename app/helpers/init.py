import time
from app.helpers.db_connection import db

reset = False
db = db()
conn = None

# Restart connection attempt permanently
while True:
    try:
        conn, error = next(db) if not reset else db.send('restart')

        if not conn:
            raise Exception(error)

        break
    except Exception as error:
        # print("ERROR: Database connection failed")
        print("ERROR", error)

        reset = True

        print("")
        time.sleep(5)

# print(conn)
# # print(next(cnx))
# cursor = conn.cursor(dictionary=True)
# query = ("SELECT NOW() as time_now")
# cursor.execute(query)
# print(cursor.fetchone())
# # print(cnx)
