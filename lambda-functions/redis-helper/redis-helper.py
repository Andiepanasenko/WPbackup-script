#!/usr/bin/env python3


import os
import sys

sys.path.append('./package')

import mysql.connector

DB_CONFIG = {
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'host': os.environ.get('MYSQL_HOST'),
    'port': os.environ.get('MYSQL_PORT', 3306),
    'database': os.environ.get('MYSQL_DATABASE')
}

CREATE_REDIS_TABLE = (
    "CREATE TABLE  IF NOT EXISTS {} ("
    "  `id` INT(3) UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  `service_name` VARCHAR(64) NOT NULL,"
    "  `database_number` SMALLINT UNSIGNED NOT NULL UNIQUE,"
    "  `removed`  TINYINT(1) NOT NULL DEFAULT 0)"
)

SELECT_TARGET_SERVICE = (
    "SELECT database_number from {} "
    "WHERE service_name = %s AND removed = 0"
)

SELECT_FREE_DB = (
    "SELECT id, database_number from {} where removed = 1"
)

UPDATE_FREE_DB = (
    "UPDATE {} SET service_name = %s, removed = 0 WHERE id = %s"
)

SET_DATABASE_NUMBER = (
    "SET @index = (SELECT MAX(`database_number`) + 1 FROM {})"
)

GET_DATABASE_NUMBER = (
    "SELECT @index"
)

INSERT_DATABASE_NUMBER = (
    "INSERT INTO {} (service_name, database_number) VALUES(%s,%s)"
)

UPDATE_FREE_UP_DB = (
    "UPDATE {} SET removed = 1 WHERE service_name = %s"
)


def handler(event, context):
    service_name = event.get('service_name')
    redis_host = event.get('redis_host')
    operation = event.get('operation','apply')

    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f'Failed connecting to database: {err}')
        exit(1)

    cursor = cnx.cursor(buffered=True)

    if operation == 'destroy':
        cursor.execute(UPDATE_FREE_UP_DB.format(redis_host), (service_name,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return {'database_number': None}

    cursor.execute(CREATE_REDIS_TABLE.format(redis_host))

    cursor.execute(SELECT_TARGET_SERVICE.format(redis_host), (service_name,))

    created_db = cursor.fetchone()

    if created_db is not None:
        print(f'Service is configured for database {created_db[0]}')
        cursor.close()
        cnx.close()
        return {'database_number': str(created_db[0])}

    cursor.execute(SELECT_FREE_DB.format(redis_host))

    free_db = cursor.fetchone()

    if free_db is not None:
        # free_db[0] = id, free_db[1] = database_number
        cursor.execute(UPDATE_FREE_DB.format(redis_host), (service_name, free_db[0]))
        target_db = free_db[1]
        print(f'Update Redis DB is {target_db}')

    else:
        cursor.execute(SET_DATABASE_NUMBER.format(redis_host))
        cursor.execute(GET_DATABASE_NUMBER)
        db_number = cursor.fetchone()[0]
        target_db = db_number if db_number is not None else 1
        cursor.execute(INSERT_DATABASE_NUMBER.format(redis_host), (service_name, target_db))
        print(f'Insert Redis DB {target_db}')

    cnx.commit()

    cursor.close()
    cnx.close()

    return {'database_number': str(target_db)}

if __name__ == '__main__':
    event = {'service_name': sys.argv[1], 'redis_host': sys.argv[2]}
    redis_ns = handler(event, None)
    print(redis_ns)
