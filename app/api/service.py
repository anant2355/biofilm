import os
import sys
import pymysql
from core.logger import get_logger
from app.api.process import Process
from flask import jsonify, make_response

logger = get_logger(__name__)
processor=Process()
app=processor.get_app()

def db_conn():
    try:
        connection = pymysql.connect(host=processor.args.db_host_name,
                                     user=processor.args.db_user,
                                     password=processor.args.db_paswd,
                                     database=processor.args.db_name,
                                     cursorclass=pymysql.cursors.DictCursor)
            
            
        if(connection):
            logger.info('Connection created successfully')
        return connection
    except Exception as e:
            logger.error(f"While processing in Function {db_conn.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")

@app.route('/db', methods=['GET'])            
def return_db():
    try:
        connection = db_conn()
        with connection.cursor() as cur:
            cur.execute("select * from Biofilm.organisms limit 5;")
            results = cur.fetchall()
            cur.close()
        return results
    
    except Exception as e:
            logger.error(f"While processing in Function {return_db.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        

