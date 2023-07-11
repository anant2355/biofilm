-- drop table biofilm_images

CREATE TABLE biofilm_images (
  image_id VARCHAR(50) NOT NULL, -- A unique identifier to the image file
  image_location VARCHAR(255) NOT NULL, -- location online where the image is located
  capture_date DATETIME NOT NULL, --  date time when the image is captured
  resolution VARCHAR(20), -- dimensions of the image
  format VARCHAR(10), --  file format of the image (e.g., JPEG, PNG)
  size INT, -- file size of the image
  annotations TEXT, -- textual annotations or labels added to the image
  study_name VARCHAR(100), -- name of the study or experiment
  researcher_name VARCHAR(100), -- name of the researcher associated with the image
  created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP, -- current timestamp when a record is created 
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- updated timestamp of the record
  INDEX idx_users_updated_at (updated_at),  -- improve query performance when filtering or sorting based on the updated_at column
  PRIMARY KEY (image_id)
);