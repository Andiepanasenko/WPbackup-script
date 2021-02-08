import os
import argparse
from datetime import datetime
from configparser import RawConfigParser
from pyzabbix import ZabbixMetric
from pyzabbix import ZabbixSender

if __name__ == '__main__':
    #
    # Parse script args
    #

    root_dir = os.path.dirname(__file__)
    config_file = os.path.join(root_dir, "config.cfg")

    parser = argparse.ArgumentParser()
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
        ZB_SERVER = config[section]['ZB_SERVER']
        ZB_PORT = int(config[section]['ZB_PORT'])
        ZB_HOST = config[section]['ZB_HOST']
        ALLOWED_WORK_TIME = int(config[section]['ALLOWED_WORK_TIME'])


        max_work_time = 0
        zbx_packet = []


        raw_data = os.popen('ps aux | grep resque-1').read()
        for i in raw_data.split('\n'):
            # Data normalization
            try:
                proc_data = ' '.join(i.split()).split(' ')
                time = proc_data[9].split(':')
            except:
                continue

            proc_id = proc_data[1]
            proc_time_work = int(time[0]) * 60 + int(time[1])

            if max_work_time < proc_time_work:
                max_work_time = proc_time_work
            
            if proc_time_work >= ALLOWED_WORK_TIME:
                zbx_packet.append(ZabbixMetric(ZB_HOST, 'resque.freeze.killed_proc_data', proc_data))
                os.system('kill ' + proc_id)


        zbx_packet.append(ZabbixMetric(ZB_HOST, 'resque.freeze.max_work_time', max_work_time))

        #
        # Send a packet with metrics to Zabbix
        #
        zbs = ZabbixSender(zabbix_server=ZB_SERVER, zabbix_port=ZB_PORT)
        print(zbs.send(zbx_packet))
