-- drop table Biofilm.image_data;
-- drop table Biofilm.experiment;

CREATE TABLE Biofilm.experiment (
  id INT NOT NULL AUTO_INCREMENT,
  experiment_name VARCHAR(255) NOT NULL,
  project VARCHAR(255) NOT NULL, 
  lab_owner VARCHAR(255) NOT NULL, 
  organism_ncbi_id VARCHAR(255) NOT NULL,
  vessel_name VARCHAR(255) NOT NULL,
  substratum_name VARCHAR(255) NOT NULL, 
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_experiment_updated_at (updated_at),  
  PRIMARY KEY (id),
  FOREIGN KEY (lab_owner) REFERENCES labs (lab_owner),
  FOREIGN KEY (organism_ncbi_id) REFERENCES organisms (ncbi_id),
  FOREIGN KEY (vessel_name) REFERENCES vessels (vessel_name),
  FOREIGN KEY (substratum_name) REFERENCES substratum (substratum_name)
);