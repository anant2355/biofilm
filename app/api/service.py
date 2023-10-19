import io
import os
import sys
import pymysql
import paramiko
import paramiko
from PIL import Image
from core.logger import get_logger
from app.api.process import Process
from flask import request, Response, send_file, jsonify

logger = get_logger(__name__)
processor=Process()
config = processor.config
app=processor.get_app()

def db_conn():
    try:
        connection = pymysql.connect(host=processor.args.db_host_name,
                                     user=processor.args.db_user,
                                     password=processor.args.db_paswd,
                                     database=processor.args.db_name,
                                     cursorclass=pymysql.cursors.DictCursor)
            
            
        if(connection):
            logger.info('Connection to database created successfully')
        return connection
    except Exception as e:
            logger.error(f"While processing in Function {db_conn.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
def remote_server_conn():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh_client.connect(processor.args.remote_host, port=int(processor.args.remote_port), username=processor.args.remote_username, password=processor.args.remote_password)
        
        sftp = ssh_client.open_sftp() 
        
        if(ssh_client):
            logger.info('Connection to remote server created successfully')
        return ssh_client
    
    except Exception as e:
            logger.error(f"While processing in Function {remote_server_conn.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            

@app.route('/db', methods=['POST'])            
def return_db():
    try:
        limit=int(request.json['limit'])
        connection = db_conn()
        with connection.cursor() as cur:
            cur.execute(f"select * from Biofilm.organisms limit {limit};")
            results = cur.fetchall()
            cur.close()
        return results
    
    except Exception as e:
            logger.error(f"While processing in Function {return_db.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
       
        
@app.route('/get_image', methods=['GET'])            
def return_image():
    try:
        request_data = request.json
        remote_file_name = request_data['remote_file_name']
        remote_folder = config['remote_server_folder']
        remote_file_path = os.path.join(remote_folder,remote_file_name)
        
        ssh_client = remote_server_conn()
        sftp = ssh_client.open_sftp()
        
        image_data = sftp.file(remote_file_path, 'rb').read()
            
        return send_file(io.BytesIO(image_data),mimetype='image/jpeg')
    
    except Exception as e:
            logger.error(f"While processing in Function {return_image.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        
    finally:
        sftp.close()
        ssh_client.close()
        
        
@app.route('/upload_image', methods=['POST'])            
def upload_image():
    try:
        image = request.files['image']
        
        remote_folder = config['remote_server_folder']
        
        image_data = io.BytesIO(image.read())
        remote_file_path = os.path.join(remote_folder,image.filename)
        
        ssh_client = remote_server_conn()
        sftp = ssh_client.open_sftp()
        sftp.putfo(image_data, remote_file_path)
        
        logger.info(f"Image uploaded to '{remote_file_path}' on the remote server") 
        return jsonify({'message': f"Image uploaded to '{remote_file_path}' on the remote server"})
        
    except Exception as e:
            logger.error(f"While processing in Function {upload_image.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        
    finally:
        sftp.close()
        ssh_client.close()
        
        
        