-- drop table user_info

CREATE TABLE user_info (
	firstname varchar(255) not null,  -- first name of the user
    lastname varchar(255) null,  -- last name of the user
    email varchar(255) null,  -- email of the user
    username varchar(255) not null,  -- username of the user
    password varchar(255) not null,  -- password of the user
    created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,  -- current timestamp when a record is created 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- updated timestamp of the record
    INDEX idx_users_updated_at (updated_at), -- improve query performance when filtering or sorting based on the updated_at column
    PRIMARY KEY (username)
);