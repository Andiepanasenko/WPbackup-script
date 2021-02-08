# zabbix-agents

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

### 5. Escape symbols in ssh key for replace

1. Change `KEY_FOR_REPLACE` and `NEW_KEY` in `3-ssh-keys/docker-compose.yaml`

2. Run script

```bash
cd 3-ssh-keys
tar -czh . | docker build -t 3-ssh-keys -
docker-compose up
cd ..
```

### 6. Replace key

1. Copy Ansible Playbook to Bastion

```bash
BASTION=bastion-dev-pdffiller
scp -r 4-ssh-key-rotation $BASTION:~
ssh $BASTION
```

2. If have no `~/.ansible.cfg` - create it and add next:

```bash
[defaults]
host_key_checking = False
```

3. Run

```bash
cd 4-ssh-key-rotation
ansible-playbook -i hosts ssh_key_rotation.yaml
```

### 7. Remove folder with credentials on bastion

```bash
rm -rf ~/4-ssh-key-rotation
```
