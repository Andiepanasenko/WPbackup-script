# zabbix-agents

## Prerequisites

* [Docker](https://docs.docker.com/engine/installation/) >= 17.0
* [Docker-compose](https://docs.docker.com/compose/install/) >= 1.12

## Prepare region for new Zabbix cluster

### 1. Add credentials and settings

Change `config` and `credentials` files in root folder. If need change environment variables in `1-generate-file-with-host/docker-compose.yaml`.

### 2. Change Zabbix-agents in AWS ECS

```bash
docker-compose up --build
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
