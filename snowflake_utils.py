import snowflake.connector
import os, pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "DEV_WORSTCASESCENARIO_DB" 
SCHEMA_NAME = "WCS_DB_SCHEMA1"

def create_connection():

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT_NAME"],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASS'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        schema=os.environ["SNOWFLAKE_SCHEMA"]
    )
    
    return conn


def pull(query):

    conn = create_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        colnames = [x[0] for x in cursor.description]
        return pd.DataFrame(result, columns=colnames)
    
    finally:
        cursor.close()
        conn.close()


def push(table_name:str, columns:list, values:list):

    conn = create_connection()

    try:
        cursor = conn.cursor()

        full_table_name = f"{DB_NAME}.{SCHEMA_NAME}.{table_name}"
        columns_str = ', '.join(columns)
        values_str = ', '.join(['%s']*len(values))
        query = f"INSERT INTO {full_table_name} ({columns_str}) VALUES ({values_str})"

        cursor.execute(query, values)
        conn.commit()

    finally:
        cursor.close()
        conn.close()