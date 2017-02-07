\COPY home_item(id,item_name,total_count,total_available,model_number,description,location) FROM 'sample_data/Item.dat' WITH DELIMITER ',' NULL '' CSV
\COPY home_tag(id,item_id_id,tag) FROM 'sample_data/Tag.dat' WITH DELIMITER ',' NULL '' CSV
\COPY home_request(reason) FROM 'sample_data/Request.dat' WITH DELIMITER ',' NULL '' CSV