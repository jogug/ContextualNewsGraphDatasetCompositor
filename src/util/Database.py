import mysql.connector

class Database:

    connection_params = {
        "host" : "",
        "user" : "",
        "password" : "", 
        "database" : ""
    }

    def __init__(self, connection_params=None) -> None:
        if connection_params is not None:
            self.connection_params = connection_params
        self.connect()
        
    def connect(self):
        self.mydb = mysql.connector.connect(**self.connection_params)

    def disconnect(self):
        if self.mydb.is_connected():
            self.mydb.close()

    def execute(self, statement):
        '''
        Returns number affected rows
        '''
        mycursor = self.mydb.cursor()
        mycursor.execute(statement)
        self.mydb.commit()
        rowcount = mycursor.rowcount
        mycursor.close()
        return rowcount

    def fetchall(self, statement, dictionary = False):
        mycursor = self.mydb.cursor(dictionary = dictionary)
        mycursor.execute(statement)
        result = mycursor.fetchall()
        mycursor.close()
        return result

    def get_cursor(self, dictionary=False, raw=False, buffered=False):
        return self.mydb.cursor(dictionary=dictionary, raw=raw, buffered=buffered)
