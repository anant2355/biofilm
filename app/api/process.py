import os
import sys
import json
from flask import Flask
from dotenv import load_dotenv
import configargparse as argparse
from core.logger import get_logger
from flask_swagger_ui import get_swaggerui_blueprint


logger = get_logger(__name__)
load_dotenv(os.path.join(os.path.join(os.getcwd(), "biofilm.env")))


class Process():
    def __init__(self, ):
        self.args = self.get_arguments()
        self.config = self.get_config()
        
    def get_arguments(self, ):
        """
            Parse environment variables.
            :return: argument parsed
        """
        try:
            parser = argparse.ArgumentParser(description='biofilm_api')
            parser.add_argument('--db_host_name', required=True, env_var='DB_HOST')
            parser.add_argument('--db_user', required=False, env_var='DB_USER')
            parser.add_argument('--db_paswd', required=False, env_var='DB_PWD')
            parser.add_argument('--db_name', required=False, env_var='DB_NAME')
            parser.add_argument('--remote_host', required=False, env_var='REMOTE_HOST')
            parser.add_argument('--remote_port', required=False, env_var='REMOTE_PORT')
            parser.add_argument('--remote_username', required=False, env_var='REMOTE_USERNAME')
            parser.add_argument('--remote_password', required=False, env_var='REMOTE_PASSWORD')
            parser.add_argument('--default_request_rate_limit', required=False, type=int, env_var='DEFAULT_REQUEST_RATE_LIMIT', default=10)
            parser.add_argument('--config_file_name', required=False, env_var='CONFIG_FILE_NAME')
            return parser.parse_args([])
        
        except Exception as e:
            logger.error(f"While processing in Function {Process.get_arguments.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
    def get_config(self, ):
        """
            Load config variables:
            :return: configuration data
        """
        try:
            config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.args.config_file_name)
            
            with open(config_file_path, 'r') as fp:
                config = json.load(fp)

            return config
        
        except Exception as e:
            logger.error(f"While processing in Function {Process.get_config.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            raise
            
            
    def get_app(self, ):
        try:
            app = Flask(__name__)
            
            swaggerui_blueprint = get_swaggerui_blueprint(
                '/swagger',
                '/static/swagger.json',
                config = {
                    'app_name' : 'Biofilm API',
                    'validatorUrl' : None
                }
            )
            app.register_blueprint(swaggerui_blueprint,url_prefix = '/swagger')
            return app
        
        except Exception as e:
            logger.error(f"While processing in Function {Process.get_app.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            raise           
            
      