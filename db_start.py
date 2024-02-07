import os
import sys
import json
import owlready2
import pandas as pd
from dotenv import load_dotenv
from core.metrics import time_it
from core.logger import get_logger
from app.api.process import Process
from app.api.service import db_conn 


processor=Process()
config = processor.config
logger = get_logger(__name__)

class DB_start():
    def __init__(self, ):
        self.create_organisms()
        self.load_organisms()
        self.load_substratum()
        self.load_vessels()
        self.load_labs()
    
    @time_it("loading organisims from owl file ")
    def create_organisms(self, ):
        try:
            
            ont = owlready2.get_ontology(config['NCBI_taxonomy']).load()

            cell_org = []
            # go through classes until cellular organism node is found
            for c in ont.classes():
                if c.name.endswith(config['organisms_class_name']):
                    cell_org.append(c)
                    break
            cell_org = cell_org[0]
            logger.info('Found the node {} labeled {}'.format(cell_org.name, cell_org.label))

            # Find all the subclasses of cellular organism
            sub_cell_org = list(ont.search(subclass_of=cell_org))
            logger.info('Found {} subclasses of {}'.format(len(sub_cell_org), cell_org.label))

            # Get all the assumed leaf nodes
            leafs = []
            for sco in sub_cell_org:
                rank = sco.has_rank
                if len(rank) > 0 and str(rank[0]).endswith('species'):
                    leafs.append(sco)
            logger.info('Found {} nodes with has_rank ending in species'.format(len(leafs)))

            # get the names of the nodes
            l2 = ['{} | {}'.format(x.name, x.label[0]) for x in leafs]
            logger.info('Made a list of name and label for each leaf')

            good = config['good_list_header']
            bad = []

            for x in l2:
                if config['bad_list'][0] in x.lower():
                    bad.append(x)
                elif config['bad_list'][1] in x.lower():
                    bad.append(x)
                elif config['bad_list'][2] in x.lower():
                    bad.append(x)
                elif config['bad_list'][3] in x.lower():
                    bad.append(x)
                elif config['bad_list'][4] in x.lower():
                    bad.append(x)
                elif config['bad_list'][5] in x.lower():
                    bad.append(x)
                else:
                    good.append(x)
            logger.info('Len all: {}'.format(len(l2)))
            logger.info('len good: {}'.format(len(good)))
            logger.info('len bad: {}'.format(len(bad)))

            with open(config['static_folder']+'/'+config['organisms_output_filename'], 'w') as f:
                f.write('\n'.join(good))

            with open(config['static_folder']+'/'+config['organisms_bad_filename'], 'w') as f:
                f.write('\n'.join(bad))
                
        except Exception as e:
            logger.error(f"While processing in Function {DB_start.create_organisms.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
    @time_it("inserting organisms data into database")        
    def load_organisms(self, ):
        
        try:
            organisms = pd.read_csv(config['static_folder']+'/'+config['organisms_output_filename'],sep = '|')
            organisms.columns = organisms.columns.str.replace(' ', '')
            for column in organisms.columns:  
                organisms[column] = organisms[column].apply(lambda x:x.strip())
            organisms_list = organisms.values.tolist()
            organisms_list = [tuple(l) for l in organisms_list]

            connection = db_conn()
            with connection.cursor() as cur:
                # cur.execute(config['organism_truncate_query'])
                cur.executemany(config['organism_insert_query'], organisms_list)
                connection.commit()
                cur.close()
                connection.close()

        except Exception as e:
            logger.error(f"While processing in Function {DB_start.load_organisms.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
    
    @time_it("inserting substratum data into database")
    def load_substratum(self, ):
        try:
          
            substratum = open(config['static_folder']+'/'+config['substratum_output_filename'], "r").read().split('\n')
            substratum = [tuple([sub_]) for sub_ in substratum]
            
            connection = db_conn()
            with connection.cursor() as cur:
#                 cur.execute(config['substratum_truncate_query'])
                cur.executemany(config['substratum_insert_query'], substratum)
                connection.commit()
                cur.close()
                connection.close()
                
            
        except Exception as e:
            logger.error(f"While processing in Function {DB_start.load_substratum.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
    @time_it("inserting vessels data into database")
    def load_vessels(self, ):
        try:
            
            vessels = open(config['static_folder']+'/'+config['vessels_output_filename'], "r").read().split('\n')
            vessels = [tuple([vessel]) for vessel in vessels]
            
            connection = db_conn()
            with connection.cursor() as cur:
#                 cur.execute(config['vessels_truncate_query'])
                cur.executemany(config['vessels_insert_query'], vessels)
                connection.commit()
                cur.close()
                connection.close()

        except Exception as e:
            logger.error(f"While processing in Function {DB_start.load_vessels.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
    @time_it("inserting labs data into database")
    def load_labs(self, ):
        try:
            
            labs = open(config['static_folder']+'/'+config['labs_output_filename'], "r").read().split('\n')
            labs = [tuple([lab]) for lab in labs]
            
            connection = db_conn()
            with connection.cursor() as cur:
#                 cur.execute(config['labs_truncate_query'])
                cur.executemany(config['labs_insert_query'], labs)
                connection.commit()
                cur.close()
                connection.close()

        except Exception as e:
            logger.error(f"While processing in Function {DB_start.load_labs.__qualname__}, we got {sys.exc_info()[0]} Exception. \n '{e}' in Line Number {sys.exc_info()[2].tb_lineno}  File Name {os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)}")
            
            
if __name__ == "__main__":
    db_start = DB_start()
            