import os
import sys
import mysql.connector
from core.logger import get_logger
from app.api.process import Process
from flask import jsonify, make_response

logger = get_logger(__name__)
processor=Process()
app=processor.get_app()

def db_conn():
    try:
        mydb = mysql.connector.connect(
            host=processor.args.host,
            username=processor.args.username,
            password=processor.args.password)
        return mydb
    except Exception as e:
            logger.error(f"While processing in Function {db_conn.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")

@app.route('/db', methods=['GET'])            
def return_db():
    try:
        mydb = db_conn()
        cur = mydb.cursor()
        cur.execute("show databases;")
        results = cur.fetchall()
        cur.close()
        return results
    
    except Exception as e:
            logger.error(f"While processing in Function {return_db.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        

