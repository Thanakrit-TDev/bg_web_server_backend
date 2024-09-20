# import mysql.connector # type: ignore
# conn = mysql.connector.connect(
#             host='210.246.215.145',
#             user='root',
#             password='OKOEUdI1886*',
#             database='plasma'
#         )
# print(conn)
import mysql.connector
from mysql.connector import Error

connection = None
try:
    connection = mysql.connector.connect(
        host='210.246.215.145',
        database='plasma',
        user='root',
        password='OKOEUdI1886*'
    )
    print(connection.is_connected())

    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version", db_Info)

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("You're connected to database:", record)

        # Select data from the 'log' table
        cursor.execute("SELECT * FROM log ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        
        # Print the data row by row
        print("Data retrieved from the 'log' table:")
        for row in rows:
            print(row[1])

except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")


# finally:
#     if connection and connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("MySQL connection is closed")

# import mysql.connector
# from mysql.connector import Error

# try:
#     connection = mysql.connector.connect(host='210.246.215.145',
#                                          database='root',
#                                          user='OKOEUdI1886*',
#                                          password='plasma')
#     if connection.is_connected():
#         db_Info = connection.get_server_info()
#         print("Connected to MySQL Server version ", db_Info)
#         cursor = connection.cursor()
#         cursor.execute("select database();")
#         record = cursor.fetchone()
#         print("You're connected to database: ", record)

# except Error as e:
#     print("Error while connecting to MySQL", e)
# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("MySQL connection is closed")

# from sqlalchemy import create_engine

# # Replace with your actual database credentials
# username = 'root'
# password = 'OKOEUdI1886*'
# hostname = '210.246.215.145'
# database_name = 'plasma'

# # Create the database engine
# engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{hostname}/{database_name}')

# # Connect to the database
# connection = engine.connect()

# # Optional: test the connection
# try:
#     result = connection.execute("SELECT 1")
#     print("Connected to the database successfully.")
# except Exception as e:
#     print("Failed to connect to the database.")
#     print(e)
# finally:
#     connection.close()
