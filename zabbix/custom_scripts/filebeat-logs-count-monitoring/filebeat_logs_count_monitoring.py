import os
import argparse
from configparser import RawConfigParser
from pyzabbix import ZabbixMetric
from pyzabbix import ZabbixSender
from walrus import Database


def get_logs_count():
    """Returns count of strings in log file"""

    with open('/var/log/filebeat/filebeat') as f:
        new_value = sum(1 for _ in f)
    try:
        with open('count.txt', "r") as f:
            prev_value = f.read()
    except IOError:
        with open('count.txt', "w+") as f:
            prev_value = "0"
            f.write(prev_value)
    delta = abs(int(new_value) - int(prev_value))
    with open('count.txt', "w") as f:
        f.write(str(new_value))
    return delta



if __name__ == '__main__':
    #
    # Parse script args
    #

    root_dir = os.path.dirname(__file__)
    config_file = os.path.join(root_dir, "config.cfg")

    parser = argparse.ArgumentParser(description="connect to Redis DB, get performance metrics and send them to Zabbix")
    parser.add_argument('--conffile',
                        dest='config_file',
                        type=str,
                        default=config_file,
                        help='Full path to config file to be used with this script')
    args = parser.parse_args()

    #
    # Parse config file
    #

    config = RawConfigParser()
    config.read(args.config_file)

    for section in config.sections():
        DB_HOST = config[section]['DB_HOST']
        DB_PORT = int(config[section]['DB_PORT'])
        DB_INSTANCE = int(config[section]['DB_INSTANCE'])
        ZB_SERVER = config[section]['ZB_SERVER']
        ZB_PORT = int(config[section]['ZB_PORT'])
        ZB_HOST = config[section]['ZB_HOST']

        #
        # Connect to database
        #

        db_con = Database(host=DB_HOST, port=DB_PORT, db=DB_INSTANCE)

        #
        # Send a packet with metrics to Zabbix
        #

        packet = [
            ZabbixMetric(ZB_HOST, 'filebeat.logs.counts', get_logs_count()),
        ]

        zbs = ZabbixSender(zabbix_server=ZB_SERVER, zabbix_port=ZB_PORT)
