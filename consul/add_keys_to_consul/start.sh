#!/bin/sh

python3 /app/aws_rds_hosts_to_consul.py
python3 /app/aws_elasticache_to_consul.py
python3 /app/add_keys_to_consul.py
