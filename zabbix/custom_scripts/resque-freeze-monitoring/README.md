# Resque monitoring for Zabbix

## Description

This script is used to monitor resque proccesses work time. If procces freeze - kill it and send metric:

* `resque.freeze.killed_proc_data`

Also, send maximum work time of all resque processes:

* `resque.freeze.max_work_time`

## Prepare systemr


### Fill `config.cfg` with Database/Zabbix credentials

| Param name          | Purpose                                                    |
| ------------------- | ---------------------------------------------------------- |
| `ZB_SERVER`         | IP address or hostname of Zabbix server                    |
| `ZB_PORT`           | Port listened at Zabbix server                             |
| `ZB_HOST`           | Target hostname in Zabbix to push metrics                  |
| `ALLOWED_WORK_TIME` | Time in minutes. If process run longer - it will be killed |

### Install dependecies

1. Create dir in your instance.

```bash
    DIRPATH=/opt/zabbix/resque-freeze-monitoring
    mkdir -p $DIRPATH
    cd $DIRPATH
```

2. Copy script files to `$DIRPATH`.

3. Install dependecies.

```bash
    apt-get install -y python-pip
    pip install virtualenv
    virtualenv resque
    resque/bin/pip install -r requirements.txt
```

## Run the script

```bash
cd $DIRPATH && resque/bin/python redis_resque_freeze_monitoring.py --conffile /path/to/config.cfg
```

`--conffile` - optional, use if you have many configs or script and config locate not in the same folder.

## Add to crontab

```bash
* * * * * cd /opt/zabbix/resque-freeze-monitoring && resque/bin/python redis_resque_freeze_monitoring.py
```

## Sample output

```json
{"failed": 0, "chunk": 1, "total": 5, "processed": 5, "time": "0.000124"}
```
