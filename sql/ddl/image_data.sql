-- drop table Biofilm.image_data

CREATE TABLE Biofilm.image_data (
  experiment_id INT NOT NULL,
  date_taken TIMESTAMP NULL,
  release_date TIMESTAMP NULL,
  microscope_settings VARCHAR(10) NULL, 
  imager VARCHAR(255) NULL,
  description VARCHAR(1000) NULL,
  raw_file_location VARCHAR(255) NOT NULL,
  jpeg_file_location VARCHAR(255) NOT NULL, 
  created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP, 
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_imagedata_updated_at (updated_at),  
  PRIMARY KEY (jpeg_file_location),
  FOREIGN KEY (experiment_id) REFERENCES experiment (experiment_id)
);