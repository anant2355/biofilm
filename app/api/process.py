import os
import sys
from flask import Flask
from dotenv import load_dotenv
import configargparse as argparse
from core.logger import get_logger

logger = get_logger(__name__)
load_dotenv(os.path.join(os.path.join(os.getcwd(), "biofilm.env")))

class Process():
    def __init__(self, ):
        self.args = self.get_arguments()
        
    def get_arguments(self):
        """
            Parse environment variables.
            :return: argument parsed
        """
        try:
            parser = argparse.ArgumentParser(description='biofilm_api')
            parser.add_argument('--host', required=False, env_var='HOST')
            parser.add_argument('--username', required=False, env_var='USERNAME')
            parser.add_argument('--password', required=False, env_var='PASSWORD')
            parser.add_argument('--default_request_rate_limit', required=False, type=int, env_var='DEFAULT_REQUEST_RATE_LIMIT', default=10)
            return parser.parse_args([])
        
        except Exception as e:
            logger.error(f"While processing in Function {Process.get_arguments.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
            
    def get_app(self, ):
        try:
            app = Flask(__name__)
            return app
        
        except Exception as e:
            logger.error(f"While processing in Function {Process.get_app.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            raise           
            
      