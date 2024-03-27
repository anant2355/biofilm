import io
import os
import re
import sys
import czifile
import tempfile
import pymysql
import paramiko
import numpy as np
from PIL import Image
from io import BytesIO
from base64 import b64encode
from core.logger import get_logger
from app.api.process import Process
from werkzeug.utils import secure_filename
from flask import request, send_file, jsonify, Response

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
        request_form_dict = request.form.to_dict()
        request_form_dict[config['experiment_columns_order'][0]] = request_form_dict[config['experiment_columns_order'][0]].replace(' ', '').lower()
        request_form_dict[config['experiment_columns_order'][1]] = request_form_dict[config['experiment_columns_order'][1]].replace(' ', '').lower()
        uploaded_images = request.files.getlist('imageUpload') 
        image_names = []
        experiment_insert_check = True
        for image in uploaded_images:
            experiment_insert_data = [request_form_dict[k] for k in config['experiment_columns_order'] if k in request_form_dict]
            # image = request.files['imageUpload']
            filename = os.path.basename(image.filename)
            remote_folder = config['remote_server_folder']  
            project_folder = os.path.join(remote_folder,list(request_form_dict.values())[1])
            experiment_folder = os.path.join(project_folder,list(request_form_dict.values())[0])
            ncbi_number = re.findall(r'\d+', request_form_dict[config['experiment_columns_order'][3]])
            experiment_insert_data[3] = config['ncbi_prefix']+ ncbi_number[0]

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
                    czi_file_path = os.path.join(experiment_folder,'czi',secure_filename(image.filename))
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
            image_insert_data = [request_form_dict[k] for k in config['imagedata_columns_order'] if k in request_form_dict]
            if czi_:
                with tempfile.NamedTemporaryFile(suffix=".czi", delete=False) as temp_file:
                    temp_file.write(czi_data)
                sftp.put(temp_file.name, czi_file_path)
                os.remove(temp_file.name)
                image_insert_data.append(czi_file_path)
            else:
                image_insert_data.append('no czi file uploaded')

            image_insert_data.append(remote_file_path)
            connection = db_conn()
            with connection.cursor() as cur:
                # query = "SELECT experiment_id FROM Biofilm.experiment WHERE experiment_name = %s AND organism_ncbi_id = %s"
                cur.execute(config['experiment_ncbi_query'], (experiment_insert_data[0],experiment_insert_data[3]))
                result = cur.fetchone()
                if result:
                    experiment_id = int(result['experiment_id'])
                    experiment_insert_check = False
                if experiment_insert_check:
                    cur.execute(config['experiment_insert_query'],tuple(experiment_insert_data))
                    experiment_id = cur.lastrowid
                    experiment_insert_check = False
                image_insert_data.insert(0, experiment_id)
                cur.execute(config['images_insert_query'],tuple(image_insert_data))
                connection.commit()
                cur.close()
                connection.close()
            
            
            logger.info(f"Image uploaded to '{remote_file_path}' on the remote server") 
            image_names.append(filename)
        return jsonify({'message': f"Images {','.join(image_names)} uploaded on the remote server"})

        
    except Exception as e:
        logger.error(f"While processing in Function {submitform.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        return jsonify({'error': f"{e}"})

    finally:
        if(ssh_client):
            sftp.close()
            ssh_client.close()

@app.route('/searchattr', methods=['GET'])            
def search_attributes():
    try:
        searchOrganism = request.args.get('searchOrganism', '')
        connection = db_conn()
        with connection.cursor() as cur:
            # query = "SELECT * FROM Biofilm.organisms WHERE organism_name LIKE %s"
            cur.execute(config['organism_name_query'], ('%' + searchOrganism + '%',))
            organisms = cur.fetchall()
            results = []
            for organism in organisms:
                # query = """SELECT e.experiment_name, e.project, e.lab_owner, e.organism_ncbi_id,e.vessel_name, e.substratum_name, i.date_taken, i.release_date,i.microscope_settings, i.imager, i.description, i.jpeg_file_location,i.raw_file_location FROM experiment e JOIN image_data i ON e.experiment_id = i.experiment_id WHERE e.organism_ncbi_id = %s"""
                cur.execute(config['experiment_imagedata_join_query'], (organism['ncbi_id'],))
                experiment_data = cur.fetchall()
                for data in experiment_data:
                    jpeg_file_location = data['jpeg_file_location']
                    ssh_client = remote_server_conn()
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f'cat {jpeg_file_location}')
                    image_data = ssh_stdout.read()
                    encoded_image = b64encode(image_data).decode('utf-8')
                    result = {
                        'organism_name': organism['organism_name'],
                        'ncbi_id': organism['ncbi_id'],
                        'experiment_name': data['experiment_name'],
                        'project': data['project'],
                        'lab_owner': data['lab_owner'],
                        'vessel_name': data['vessel_name'],
                        'substratum_name': data['substratum_name'],
                        'date_taken': data['date_taken'],
                        'release_date': data['release_date'],
                        'microscope_settings': data['microscope_settings'],
                        'imager': data['imager'],
                        'description': data['description'],
                        'image_data': encoded_image,
                        'czi_file_location' : data['raw_file_location']
                    }
                    results.append(result)
            cur.close()
            connection.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"While processing in Function {search_attributes.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        return jsonify({'error': f"{e}"})

@app.route('/download-czi/<path:filepath>', methods=['GET'])
def download_czi(filepath):
    try:
        ssh_client = remote_server_conn()
        filename = os.path.basename(filepath)
        sftp = ssh_client.open_sftp()
        file_like_object = BytesIO()
        sftp.getfo('/'+filepath, file_like_object)
        file_like_object.seek(0)
        return Response(
                file_like_object,
                mimetype="application/octet-stream",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )

    except Exception as e:
        logger.error(f"While processing in Function {download_czi.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
        return jsonify({'error': f"{e}"})
    finally:
        if(ssh_client):
            sftp.close()
            ssh_client.close()
