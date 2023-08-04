-- drop table organisms

CREATE TABLE organisms (
    ncbi_id varchar(255) not null,  -- ncbi id
    organism_name varchar(255) null,  -- organism name
    PRIMARY KEY (ncbi_id)
);