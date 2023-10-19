-- drop table Biofilm.experiment

CREATE TABLE Biofilm.experiment (
  experiment_name VARCHAR(255) NOT NULL,
  project VARCHAR(255) NOT NULL, 
  lab_owner VARCHAR(255) NOT NULL, 
  organism_ncbi_id VARCHAR(255) NOT NULL,
  vessel_name VARCHAR(255) NOT NULL,
  substratum_name VARCHAR(255) NOT NULL, 
  created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP, 
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_updated_at (updated_at),  
  PRIMARY KEY (experiment_name),
  foreign key (lab_owner) references labs (lab_owner),
  foreign key (organism_ncbi_id) references organisms (ncbi_id),
  foreign key (vessel_name) references vessels (vessel_name),
  foreign key (substratum_name) references substratum (substratum_name)
);