import os
import json
import base64
import logging
import sys
import requests

# ===========================
# === Setup configuration ===
# ===========================

#
# Consul connection configuration
#

CONFIG_CONSUL_HTTP_ADDR = 'http://127.0.0.1:8500'
CONFIG_CONSUL_HTTP_TOKEN = None
CONFIG_CONSUL_HTTP_SSL_VERIFY = True
CONFIG_CONSUL_HTTP_SSL_CERT = None
CONFIG_CONSUL_CONSISTENCY = 'default'
CONFIG_CONSUL_DC = None

#
# Action configuration
#

CONFIG_ACTION = 'add'           # 'add' or 'remove'
CONFIG_SERVER_NAME = ''         # server name to add or remove
CONFIG_SERVER_PARAMS = ''       # server parameters
CONFIG_UPSTREAMS_KV_PORTS = {}  # dict of <consul_KV_path_to_upstream>[:<port>]
CONFIG_DEBUG_MODE = False       # debug mode

# helpers
YES_VALUES = ['yes', 'y', 'true', 'enable', 'enabled', 'on', '1']
NO_VALUES = ['no', 'n', 'false', 'disable', 'disabled', 'off', '0']

#
# Get configuration from environment
#

if os.environ.get('CONSUL_HTTP_ADDR') is not None:
    CONFIG_CONSUL_HTTP_ADDR = str(os.environ.get('CONSUL_HTTP_ADDR'))

if os.environ.get('CONSUL_HTTP_TOKEN') is not None:
    CONFIG_CONSUL_HTTP_TOKEN = str(os.environ.get('CONSUL_HTTP_TOKEN'))

if os.environ.get('CONSUL_HTTP_SSL_VERIFY') is not None:
    CONFIG_CONSUL_HTTP_SSL_VERIFY = not \
            str(os.environ.get('CONSUL_HTTP_SSL_VERIFY')).lower() in NO_VALUES

if os.environ.get('CONSUL_CONSISTENCY') is not None:
    CONFIG_CONSUL_CONSISTENCY = str(os.environ.get('CONSUL_CONSISTENCY'))

if os.environ.get('CONSUL_DC') is not None:
    CONFIG_CONSUL_DC = str(os.environ.get('CONSUL_DC'))

if os.environ.get('CONSUL_HTTP_SSL_CERT') is not None:
    CONFIG_CONSUL_HTTP_SSL_CERT = str(os.environ.get('CONSUL_HTTP_SSL_CERT'))

if os.environ.get("DEBUG") is not None:
        CONFIG_DEBUG_MODE = \
                            str(os.environ.get("DEBUG")).lower() in YES_VALUES

if os.environ.get('ACTION') is not None:
    CONFIG_ACTION = str(os.environ.get('ACTION')).lower()

if os.environ.get('SERVER_NAME') is not None:
    CONFIG_SERVER_NAME = str(os.environ.get('SERVER_NAME'))

if os.environ.get('SERVER_PARAMS') is not None:
    CONFIG_SERVER_PARAMS = str(os.environ.get('SERVER_PARAMS'))

if os.environ.get('SERVER_PARAMS') is not None:
    CONFIG_SERVER_PARAMS = str(os.environ.get('SERVER_PARAMS'))

if os.environ.get('UPSTREAMS_KV_PORTS') is not None:

    for path_port_pair in str(os.environ.get('UPSTREAMS_KV_PORTS')).split(','):

        if ':' in path_port_pair:

            parts = path_port_pair.split(':', 2)

            if parts[0].startswith('unix:'):
                CONFIG_UPSTREAMS_KV_PORTS.update({parts[0]: None})
            elif not parts[1]:
                CONFIG_UPSTREAMS_KV_PORTS.update({parts[0]: None})
            else:
                CONFIG_UPSTREAMS_KV_PORTS.update({parts[0]: int(parts[1])})

        else:

            CONFIG_UPSTREAMS_KV_PORTS.update({path_port_pair: None})

#
# Setup logging/debug
#

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
if CONFIG_DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

logger.debug(f'''Configuration:
- consul address:     {CONFIG_CONSUL_HTTP_ADDR}
- consul token:       {CONFIG_CONSUL_HTTP_TOKEN}
- consul consistency: {CONFIG_CONSUL_CONSISTENCY}
- consul datacenter:  {CONFIG_CONSUL_DC}
- consul verify:      {str(CONFIG_CONSUL_HTTP_SSL_VERIFY)}
- consul cert :       {CONFIG_CONSUL_HTTP_SSL_CERT}

- action: {CONFIG_ACTION}
- server name: {CONFIG_SERVER_NAME}
- server params: {CONFIG_SERVER_PARAMS}
- upstreams KV paths with ports:
{json.dumps(CONFIG_UPSTREAMS_KV_PORTS, indent=4)}''')

#
# Check some configuration parameters
#

if CONFIG_ACTION not in ('add', 'remove'):
    raise RuntimeError(f"Invalid action '{CONFIG_ACTION}'")

if not CONFIG_SERVER_NAME:
    raise RuntimeError(f'Server name not specified')

if not CONFIG_UPSTREAMS_KV_PORTS:
    raise RuntimeError(f'Upstreams consul KV paths not specified')

# ==================
# === Main logic ===
# ==================

params = []
if CONFIG_CONSUL_HTTP_TOKEN:
    params.append(('token', CONFIG_CONSUL_HTTP_TOKEN))
if CONFIG_CONSUL_DC:
    params.append(('dc', CONFIG_CONSUL_DC))
if CONFIG_CONSUL_CONSISTENCY in ('consistent', 'stale'):
    params.append((CONFIG_CONSUL_CONSISTENCY, '1'))

#
# Get current upstreams servers configurations
#

upstream_servers = {}

for kv_path in CONFIG_UPSTREAMS_KV_PORTS.keys():

    response = requests.get(
            f'{CONFIG_CONSUL_HTTP_ADDR}/v1/kv/{kv_path}',
            params=params,
            verify=CONFIG_CONSUL_HTTP_SSL_VERIFY,
            cert=CONFIG_CONSUL_HTTP_SSL_CERT)
    servers = json.loads(
            base64.b64decode(response.json()[0]['Value']).decode('utf-8'))

    if type(servers) != list:
        raise RuntimeError("Invalid servers list in '{0:s}':\n{1:s}".format(
            kv_path,
            json.dumps(servers, indent=4)))

    upstream_servers.update({kv_path: servers})

logger.debug(f'''Current upstreams server configurations:
{json.dumps(upstream_servers, indent=4)}''')


# function for filtering
def is_this_server(
        entry: str,
        server: str,
        port: int = None) -> bool:
    """Check if 'entry' corresponds to 'server' and 'port'"""
    if server.startswith('unix:') or port is None:
        return entry.strip().split()[0] == server
    else:
        return entry.strip().split()[0] == f'{server}:{port}'


#
# Remove server from upstreams
#

if CONFIG_ACTION == 'remove':
    for kv_path, port in CONFIG_UPSTREAMS_KV_PORTS.items():
        upstream_servers[kv_path] = list(filter(
            lambda e: not is_this_server(e, CONFIG_SERVER_NAME, port),
            upstream_servers[kv_path]))

#
# Add (or update) server to (in) upstreams
#

if CONFIG_ACTION == 'add':
    for kv_path, port in CONFIG_UPSTREAMS_KV_PORTS.items():

        if port:
            new_srv_ent = f'{CONFIG_SERVER_NAME}:{port} {CONFIG_SERVER_PARAMS}'
        else:
            new_srv_ent = f'{CONFIG_SERVER_NAME} {CONFIG_SERVER_PARAMS}'

        was_here = False

        for i, e in enumerate(upstream_servers[kv_path]):
            if is_this_server(e, CONFIG_SERVER_NAME, port):
                was_here = True
                upstream_servers[kv_path][i] = new_srv_ent

        if not was_here:
            upstream_servers[kv_path].append(new_srv_ent)

logger.debug(f'''Updated upstreams server configurations:
{json.dumps(upstream_servers, indent=4)}''')

#
# Update KV in consul
#

txn_data = [
        {
            'KV': {
                'Verb': 'set',
                'Key': kv_path,
                'Value': base64.b64encode(
                        json.dumps(servers).encode('utf-8')
                    ).decode('utf-8')

            }
        } for kv_path, servers in upstream_servers.items()
    ]

logger.debug(f'''TXN data:
{json.dumps(txn_data, indent=4)}''')

requests.put(
        f'{CONFIG_CONSUL_HTTP_ADDR}/v1/txn',
        data=json.dumps(txn_data),
        params=params,
        verify=CONFIG_CONSUL_HTTP_SSL_VERIFY,
        cert=CONFIG_CONSUL_HTTP_SSL_CERT)
