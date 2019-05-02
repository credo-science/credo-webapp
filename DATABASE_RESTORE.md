create database credo character set = 'utf8mb4';
GRANT ALL PRIVILEGES ON *.* TO 'credo'@'localhost' IDENTIFIED BY 'credo-db-password';


docker exec -it credo-webapp ./manage.py rqworker default data_export low
docker exec -it credo-webapp ./manage.py refresh_data
