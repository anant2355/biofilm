-- drop table Biofilm.organisms

CREATE TABLE Biofilm.organisms (
    ncbi_id varchar(255) not null,  -- ncbi id
    organism_name varchar(255) not null,  -- organism name
    PRIMARY KEY (ncbi_id)
);