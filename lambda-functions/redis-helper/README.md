Function for redis databases management: services require separate redis database for every used redis instance.
Information about service-database_number pair are stored in the MySQL tables (table per redis instance).

Table rows example.
```
+----+-----------------+-----------------+---------+
| id | service_name    | database_number | removed |
+----+-----------------+-----------------+---------+
|  1 | api-permissions |               1 |       0 |
+----+-----------------+-----------------+---------+

```

Input json map keys:
* service_name  - application service name
* redis_host - table will be created with this name
* operation - apply(create table, insert values) or destroy(set removed value to 1)

Environment variables:
* MYSQL_USER 
* MYSQL_PASSWORD
* MYSQL_HOST
* MYSQL_DATABASE
* MYSQL_PORT, not mandatory, default 3306

Needed additional python packages are specified in requirements.txt file. Install them to `package` directory
```
pip3 install -r requirements.txt --target ./package
```
https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

Zipped deploy package is mandatory.