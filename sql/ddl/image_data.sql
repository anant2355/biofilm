-- drop table Biofilm.image_data

CREATE TABLE Biofilm.image_data (
  experiment_name VARCHAR(255) NOT NULL,
  image_file_location VARCHAR(255) NOT NULL, 
  date_taken TIMESTAMP NULL, 
  release_date TIMESTAMP NULL, 
  imager VARCHAR(255) NULL,
  microscope_settings json NULL, 
  description VARCHAR(1000) NULL,
  raw_data_location VARCHAR(255) NOT NULL,
  created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP, 
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_updated_at (updated_at),  
  PRIMARY KEY (image_file_location),
  foreign key (experiment_name) references Biofilm.experiment(experiment_name)
);