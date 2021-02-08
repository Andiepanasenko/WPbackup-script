## Generate json-files and add keys to Consul
Local:
```bash
scp -r ./add_keys_to_consul  USER@AWS_IP:~
```

Consul container on EC2 instance:
```bash
ifconfig eth0
```

On EC2 instance:
```bash
cd add_keys_to_consul
vi Dockerfile
# change IP and add AWS keys

docker build .
docker run --rm
```

### MySQL

In `remote-monitor//RDS` add passwords for:
* `lb-rds-2`
* `lb-rds-ro`
* `lb-rds-fast-ro`

Add users and passwords for them
### RabbitMQ

In `remote-monitor//rabbitmq` create:
* `user`
* `password`

### Zabbix
In `remote-monitor//zabbix` create:
* `user`
* `password`

In `remote-monitor//zabbix/hostnames` create:
* hostnames for `dfs` (`dfs/dfs=remote-monitor-dfs`)
* hostnames for `elasticsearch` (`elasticsearch/elasticsearch=remote-monitor-elasticsearch`)
* hostnames for `rabbitmq` (`rabbitmq/rabbitmq=remote-monitor-rabbitmq`)
* hostnames for `redis-io` (`redis-io/redis-io=remote-monitor-redis`)


Change Redis hostnames:
* php-public-api -> `remote-monitor-redis-api`
* prod-websocket-2 -> `remote-monitor-redis-websocket`
* websocket2-big -> `remote-monitor-redis-websocket`
* websocket -> `remote-monitor-redis-websocket`
* ws-pdf-services2 -> `remote-monitor-redis-websocket`
* ws-pdf-services -> `remote-monitor-redis-websocket`
