select * from Biofilm.experiment;

select * from Biofilm.image_data;

select * from Biofilm.organisms; 

select * from Biofilm.substratum;

select * from Biofilm.labs;

select * from Biofilm.vessels;

select * from Biofilm.organisms where organism_name like '%Nocardia sp.%'; 

SELECT e.experiment_name, e.project, e.lab_owner, e.organism_ncbi_id,e.vessel_name, e.substratum_name, 
i.date_taken, i.release_date,i.microscope_settings, i.imager, i.description FROM 
experiment e JOIN image_data i ON e.experiment_name = i.experiment_name  WHERE e.organism_ncbi_id = 'NCBITaxon_1000003';


