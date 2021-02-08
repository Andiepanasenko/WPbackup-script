# Filebeat monitoring for Zabbix

## Description

This script is used connect to specified Redis DB, get the count of records in log-file Filebeat and send them to Zabbix:

* `filebeat.logs.counts`


## Prepare system

### Fill `config.cfg` with Database/Zabbix credentials

| Param name    | Purpose                                   |
| ------------- | ----------------------------------------- |
| `DB_HOST`     | Redis DB hostname                         |
| `DB_PORT`     | Port listened at Redis DB                 |
| `DB_INSTANCE` | Redis Database used for query             |
| `ZB_SERVER`   | IP address or hostname of Zabbix server   |
| `ZB_PORT`     | Port listened at Zabbix server            |
| `ZB_HOST`     | Target hostname in Zabbix to push metrics |

### Install dependecies

1. Create dir in your instance.
```bash
    DIRPATH=/opt/zabbix/filebeat-monitoring
    mkdir $DIRPATH
    cd $DIRPATH
```

2. Copy script files to `$DIRPATH`.

3. Install dependencies.

```bash
    pip install virtualenv
    virtualenv filebeat
    pip install -r requirements.txt
```

## Run the script

```bash
cd $DIRPATH && filebeat/bin/python filebeat_logs_count_monitoring.py --conffile /path/to/config.cfg
```

`--conffile` - optional, use if you have many configs or script and config locate not in the same folder.