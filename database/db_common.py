from dotenv import load_dotenv
import mysql.connector
import os

HOST = ""
USER = ""
PASSWORD = ""
DATABASE = ""

#load_dotenv()

def getDB():
    """
    getDB is used to get a sql connector for the db defined in the env file

    :return: db connection
    """
    dbConnection = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    return dbConnection

def commitQuery(query):
    """
    commitQuery is used to update items in the database

    :param query: SQL query to be run against the DB
    """
    db = getDB()
    cursor = db.cursor(prepared=True, dictionary=True)
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()

def grabQuery(query):
    """
    grabQuery is used to grab data from the DB

    :param query: SQL query to be run against the DB
    :return: returns the output of the query in dictionary format
    """
    db = getDB()
    cursor = db.cursor(prepared=True, dictionary=True)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data