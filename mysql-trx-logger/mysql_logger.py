#!/usr/bin/env python
import MySQLdb
import json
import datetime
import ConfigParser
import sys
import time
import logging.handlers

config = ConfigParser.ConfigParser()
config.read("./settings/config.ini")

queryes = tuple(("select *, md5(trx_query) as trx_query_md5, md5(trx_id) as trx_id_md5, 'INNODB_TRX' as query_type from information_schema.innodb_trx;",
                "SELECT *, md5(lock_trx_id) as trx_id_md5, 'INNODB_LOCKS' as query_type FROM INFORMATION_SCHEMA.INNODB_LOCKS;",
                "SELECT *, md5(blocking_trx_id) as trx_id_md5, 'INNODB_LOCK_WAITS' as query_type FROM INFORMATION_SCHEMA.INNODB_LOCK_WAITS;",
                """SELECT r.trx_id AS waiting_trx_id,
                'STUCKED_TRANSACTIONS' as query_type, 
                r.trx_mysql_thread_id AS waiting_thread,       
                TIMESTAMPDIFF(SECOND, r.trx_wait_started, CURRENT_TIMESTAMP) AS wait_time,       
                r.trx_query AS waiting_query,       
                l.lock_table AS waiting_table_lock,       
                b.trx_id AS blocking_trx_id, 
                b.trx_mysql_thread_id AS blocking_thread,       
                SUBSTRING(p.host, 1, INSTR(p.host, ':') - 1) AS blocking_host,       
                SUBSTRING(p.host, INSTR(p.host, ':') +1) AS blocking_port,       
                IF(p.command = "Sleep", p.time, 0) AS idle_in_trx,       
                b.trx_query AS blocking_query FROM INFORMATION_SCHEMA.INNODB_LOCK_WAITS AS w 
                    INNER JOIN INFORMATION_SCHEMA.INNODB_TRX AS b ON b.trx_id = w.blocking_trx_id 
                    INNER JOIN INFORMATION_SCHEMA.INNODB_TRX AS r ON r.trx_id = w.requesting_trx_id 
                    INNER JOIN INFORMATION_SCHEMA.INNODB_LOCKS AS l ON w.requested_lock_id = l.lock_id 
                    LEFT JOIN INFORMATION_SCHEMA.PROCESSLIST AS p ON p.id = b.trx_mysql_thread_id ORDER BY wait_time DESC;"""))

STDOUT_LOG_FILENAME = config.get('logs_path', 'stdout')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.handlers.TimedRotatingFileHandler(STDOUT_LOG_FILENAME, when="midnight", backupCount=3)
logger.addHandler(stdout_handler)

class logs(object):
        def __init__(self, logger, level):
                self.logger = logger
                self.level = level
        def write(self, message):
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

sys.stdout = logs(logger, logging.INFO)

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def select_trx():
    try:
        db = MySQLdb.connect(host=config.get('db', 'host'),
                             user=config.get('db', 'user'),
                             passwd=config.get('db', 'passwd'))
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        db.close()
        sys.exit(1)

    cur = db.cursor()
    while True:
        for i in queryes:
            try:
                cur.execute(i)
            except (MySQLdb.Error, MySQLdb.Warning) as e:
                print(e)
                cur.close()
                db.close()
                sys.exit(1)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                result = cur.fetchall()
                for row in result:
                    raw_computed = dict(zip(columns, row))
                    print(json.dumps(raw_computed, default=datetime_handler))
        time.sleep(int(config.get('db', 'timeout')))

if __name__ == '__main__':
    try:
        select_trx()
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt".format(e))
        sys.exit(1)
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)