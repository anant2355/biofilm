-- drop table user_mapping

CREATE TABLE user_mapping (
	id INT AUTO_INCREMENT PRIMARY KEY,  -- auto incrementing primary key
    username varchar(255) not null, -- username of the user and also a foreign key to username in user_info table
    credentials boolean DEFAULT false, -- whether the user has credentials to upload the image or not
    created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP, -- current timestamp when a record is created 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- updated timestamp of the record
    INDEX idx_users_updated_at (updated_at),  -- improve query performance when filtering or sorting based on the updated_at column
    FOREIGN KEY (username) REFERENCES user_info(username)
);