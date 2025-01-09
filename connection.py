import mysql.connector


def initialize_db(server, username, password, database_name):
    """
    Initializes a connection to the MySQL database.

    Args:
        server (str): The address of the database server.
        username (str): The username for database authentication.
        password (str): The password for database authentication.
        database_name (str): The name of the database to connect to.

    Returns:
        mysql.connector.connection: A connection object if successful, or None if there is an error.

    Raises:
        ValueError: If any of the required fields are missing.
    """
    if not all([server, username, password, database_name]):
        raise ValueError("All field must be filled")
    try:
        mydb = mysql.connector.connect(
            host=server,
            user=username,
            password=password,
            database=database_name
        )
        return mydb
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")
        return None
