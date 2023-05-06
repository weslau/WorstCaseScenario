import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

def create_snowflake_connection():

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT_NAME"],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASS'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        schema=os.environ["SNOWFLAKE_SCHEMA"]
    )
    
    return conn

def query_snowflake(query):

    conn = create_snowflake_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    
    finally:
        cursor.close()
        conn.close()
