import pymysql

# Replace these values with your actual database credentials
db_config = {
    "host": "mysql-imex.alwaysdata.net",
    "user": "imex_2",
    "password": "123456@galib",
    "database": "imex_etsy",
    "port": 3306,
}

try:
    # Attempt to establish a connection
    conn = pymysql.connect(**db_config)

    # If successful, print a success message
    if conn.open:
        print("Connected to MySQL database")

    # Close the connection
    conn.close()

except pymysql.Error as e:
    # Handle any errors that occurred during the connection attempt
    print(f"Error: {e}")
