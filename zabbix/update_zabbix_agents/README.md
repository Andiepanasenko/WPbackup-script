# Update zabbix agents

## Prerequisites

* [Docker](https://docs.docker.com/engine/installation/) >= 17.0
* [Docker-compose](https://docs.docker.com/compose/install/) >= 1.12

## Prepare region for new Zabbix cluster

### 1. Add credentials and settings

Change `config` and `credentials` files in root folder. If need change environment variables in `1-generate-file-with-host/docker-compose.yaml`.

### 2. Generate file with hosts for ansible and boto3

```bash
cd 1-generate-file-with-host
tar -czh . | docker build -t 1-generate-file-with-host -
docker-compose up
cd ..
```

### 3. Review hosts file

Look on `hosts` file in root folder and if find useless hosts - add them to `1-generate-file-with-host/ignored_mask.py` and restart script

### 4. Add Security Group for hosts

1. Change `SECURITY_GROUP` in `docker-compose.yaml` to default SG, also know in Terraform workl as SG `default_vpc`.

2. Run script

```bash
cd 2-add-sg-for-instances
tar -czh . | docker build -t 2-add-sg-for-instances -
docker-compose up
cd ..
```

### 5. Update/Install Zabbix Agents

1. Change `Server` and `ServerActive` in `3-add-zabbix-agents/zabbix_agentd.conf`.

2. Copy Ansible Playbook to Bastion and run

```bash
BASTION=bastion-dev
scp -r 3-add-zabbix-agents $BASTION:~
ssh $BASTION

cd 3-add-zabbix-agents
ansible-playbook -i hosts zabbix-agents.yaml
```

### 6. Remove folder with credentials on bastion

```bash
rm -rf ~/3-add-zabbix-agents
```

### 7. Change Zabbix-agents in AWS ECS

1. Change env variables in `4-update-task-def-in-clusters/docker-compose.yaml`

2. Run

```bash
cd 4-update-task-def-in-clusters
tar -czh . | docker build -t 4-update-task-def-in-clusters -
docker-compose up
cd ..
```

#### Typical structure of Task Definition

```python
{'containerDefinitions': [
        {'name': 'dev-zabbix-agent', 'image': 'zabbix/zabbix-agent:alpine-trunk', 'cpu': 64, 'memory': 64, 'portMappings': [
                {'containerPort': 10050, 'hostPort': 10050, 'protocol': 'tcp'
                }
            ], 'essential': True, 'environment': [
                {'name': 'ZBX_DEBUGLEVEL', 'value': '4'
                },
                {'name': 'ZBX_SERVER_PORT', 'value': '10050'
                },
                {'name': 'ZBX_METADATA', 'value': 'Docker Linux ECS us-east-1 dev-zabbix-agent'
                },
                {'name': 'ZBX_SERVER_HOST', 'value': 'zabbix-server.pdf.int,internal-dev-zabbix-server-1655492707.us-east-1.elb.amazon'
                }
            ], 'mountPoints': [
                {'sourceVolume': 'root', 'containerPath': '/rootfs', 'readOnly': True
                },
                {'sourceVolume': 'var_run', 'containerPath': '/var/run', 'readOnly': False
                }
            ], 'volumesFrom': [], 'privileged': True
        }
    ], 'family': 'dev-zabbix-agent', 'networkMode': 'host', 'volumes': [
        {'name': 'root', 'host': {'sourcePath': '/'
            }
        },
        {'name': 'var_run', 'host': {'sourcePath': '/var/run'
            }
        }
    ], 'placementConstraints': [], 'requiresCompatibilities': []
}
```