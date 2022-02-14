from db_connection import cnx as conn


def execute_query(query):
    print(conn)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)

    # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html
    conn.commit()

    # https: // dev.mysql.com / doc / connector - python / en / connector - python - api - mysqlconnection -
    # rollback.html
    # conn.rollback()

    cursor.close()

# def get_records