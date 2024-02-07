import io
import os
import sys
import czifile
import tempfile
import pymysql
import paramiko
import numpy as np
from PIL import Image
from core.logger import get_logger
from app.api.process import Process
from werkzeug.utils import secure_filename
from flask import request, send_file, jsonify

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
                
        if(ssh_client):
            logger.info('Connection to remote server created successfully')
        return ssh_client
    
    except Exception as e:
        logger.error(f"While processing in Function {remote_server_conn.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
        
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
        
def create_dir(experiment_folder,ssh_client):
    try:
        create_command = "mkdir -p {}"
        create_command_jpeg = create_command.format(os.path.join(experiment_folder,'jpeg'))
        stdin, stdout, stderr = ssh_client.exec_command(create_command_jpeg)
        create_command_czi = create_command.format(os.path.join(experiment_folder,'czi'))
        stdin, stdout, stderr = ssh_client.exec_command(create_command_czi)

    except Exception as e:
        logger.error(f"While processing in Function {create_dir.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")


def return_dir(project_folder,experiment_folder):
    try:
        ssh_client = remote_server_conn()
        check_command = "[ -d '{}' ] && echo 'Directory exists' || echo 'Directory does not exist'"
        check_command_proj = check_command.format(project_folder)
        check_command_exp = check_command.format(experiment_folder)
        _, stdout, _ = ssh_client.exec_command(check_command_proj)
        directory_status_proj = stdout.read().decode('utf-8').strip()
        _, stdout, _ = ssh_client.exec_command(check_command_exp)
        directory_status_exp = stdout.read().decode('utf-8').strip()
        if directory_status_proj == 'Directory does not exist' : 
            create_dir(experiment_folder,ssh_client)
            
        elif directory_status_proj == 'Directory exists' and directory_status_exp == 'Directory does not exist':
            create_dir(experiment_folder,ssh_client)

    except Exception as e:
        logger.error(f"While processing in Function {return_dir.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")

    finally:
        ssh_client.close()
       

@app.route('/submitform', methods=['POST'])            
def submitform():
    try:
        request_form = list(request.form.to_dict().values())
        experiment_insert_data = request_form[:6]
        image = request.files['imageUpload']
        filename = os.path.basename(image.filename)
        remote_folder = config['remote_server_folder']  
        project_folder = os.path.join(remote_folder,request_form[1])
        experiment_folder = os.path.join(project_folder,request_form[0])

        czi_ = False
        if os.path.splitext(filename)[1] == '.czi':
            czi_data = czifile.imread(io.BytesIO(image.read()))
            for i, scene in enumerate(czi_data):
                scaled_data = (scene * 255.0 / scene.max()).astype(np.uint8)
                img = Image.fromarray(scaled_data)
                filename = filename.split('.')[0]+'.jpeg'
                image_data = io.BytesIO()
                img.save(image_data, format='JPEG')
                image_data.seek(0)
                czi_ = True

        elif os.path.splitext(filename)[1] == '.jpeg':
            image_data = io.BytesIO(image.read())
        else:
            return jsonify({'message': f"Image uploaded should be in format czi/jpeg"})

        return_dir(project_folder,experiment_folder)
        ssh_client = remote_server_conn()
        remote_file_path = os.path.join(experiment_folder,'jpeg',filename)
        sftp = ssh_client.open_sftp()
        sftp.putfo(image_data, remote_file_path)
        if czi_:
            with tempfile.NamedTemporaryFile(suffix=".czi", delete=False) as temp_file:
                temp_file.write(czi_data)
            sftp.put(temp_file.name, os.path.join(experiment_folder,'czi',secure_filename(image.filename)))
            os.remove(temp_file.name)

        image_insert_data = [request_form[0]]+ [remote_file_path] + request_form[6:8] + [request_form[2]] + [request_form[8]] + [request_form[9]] + [remote_file_path]
        connection = db_conn()
        with connection.cursor() as cur:
            cur.execute(config['experiment_insert_query'],tuple(experiment_insert_data))
            cur.execute(config['images_insert_query'],tuple(image_insert_data))
            connection.commit()
            cur.close()
            connection.close()
        
        
        logger.info(f"Image uploaded to '{remote_file_path}' on the remote server") 
        return jsonify({'message': f"Image uploaded to '{remote_file_path}' on the remote server"})
        
    except Exception as e:
        logger.error(f"While processing in Function {submitform.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        return jsonify({'error': f"{e}"})

    finally:
        if(ssh_client):
            sftp.close()
            ssh_client.close()