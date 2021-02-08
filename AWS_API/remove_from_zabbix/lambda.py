#!/usr/bin/env python3.7

import os

import boto3
from pyzabbix import ZabbixAPI
from slackmessage import send_message_to_slack

ec2 = boto3.client('ec2')


def getInstanceName(tags):
    """
        Searches for a value of 'Name' tag given the list of tags

        :type tags: obj
    """
    instancename = ''
    for tag in tags:
        if tag['Key'] == 'Name':
            instancename = tag['Value']
    return instancename


def zabbix_host_name(ec2_name, ec2_ip_address):
    """
        Constructs hostname as should be defined in Zabbix according
            to naming convention

        :type ec2_name: str
        :param ec2_name: EC2 Instance name as defined in tags

        :type ec2_ip_address: str
        :param ec2_ip_address: EC2 Instance private IP address
    """
    zhostname = "{}-ip-{}".format(
        ec2_name,
        ec2_ip_address.replace('.', '-')
    )
    return zhostname


def lambda_handler(event, context):
    event_source = event["source"]

    # Receive a list of resources by state
    resources = ec2.describe_instances(
        Filters=[{
            'Name': 'instance-state-name',
            'Values': ['terminating']}])

    """
        Search for private IP addresses of hosts to remove

        Dictionary hosts_for_removal={ 'ip_address': 'hostname' }
            is used to store information
    """
    hosts_for_removal = {}

    for reservation in resources['Reservations']:
        for instance in reservation['Instances']:
            ip_address = ''
            for interface in instance['NetworkInterfaces']:
                ip_address = interface['PrivateIpAddress']
            zabbix_host = zabbix_host_name(
                getInstanceName(instance['Tags']), ip_address)
            hosts_for_removal[ip_address] = zabbix_host

    msg_hosts = '\n'.join(
        ("`{}`, _{}_".format(*i) for i in hosts_for_removal.items()))

    send_message_to_slack(
        "Will remove the following EC2 instances from Zabbix:\
         \n{}".format(msg_hosts),
        msg_source=event_source,
        msg_type='info')

    # Zabbix API target and credentials
    zapi = ZabbixAPI(
        os.getenv('ZABBIX_API_URL'),
        user=os.getenv('ZABBIX_API_LOGIN'),
        password=os.getenv('ZABBIX_API_PASSWD'))

    """
        Retrieve a list of hostids for removal in Zabbix

        List hosts_in_zabbix = [] is used to store information
    """
    hosts_in_zabbix = []
    zhostnames = {}

    hostids = zapi.hostinterface.get(
        filter={"ip": list(hosts_for_removal.keys())},
        output='extend')

    for id in hostids:
        hosts_in_zabbix.append(id['hostid'])
        zhostnames[id['ip']] = id['hostid']

    """
        Search for naming mismatches. If mismatch found
            remove hostid from the list hosts_in_zabbix.
    """
    hosts_before = len(hosts_in_zabbix)

    znames = zapi.host.get(
        filter={"hostid": hosts_in_zabbix},
        output='extend')
    removed_hosts = []

    for zname in znames:
        for key, value in zhostnames.items():
            if zhostnames[key] == zname['hostid']:
                buf = zhostnames[key]
                zhostnames[key] = zname['host']
                removed_hosts.append(zname['host'])
            else:
                continue
            if hosts_for_removal[key] != zname['host']:
                print("[WARN][Will Not Remove] Names mismatch found: "
                      "IP {} Hostname {} | Expected Hostname: {}. "
                      "Please remove manually".format(
                          key,
                          zname['host'],
                          hosts_for_removal[key]))
                hosts_in_zabbix.remove(buf)

    hosts_after = len(hosts_in_zabbix)

    msg_rm = '\n'.join((f"_{i}_" for i in removed_hosts))

    zapi.do_request('host.delete', params=hosts_in_zabbix)

    send_message_to_slack(
        "Removed hosts from Zabbix: \n{}".format(msg_rm),
        msg_source=event_source,
        msg_type='info')

    if hosts_after < hosts_before:
        send_message_to_slack(
            "Queued for removal {} items, removed {} items. "
            "Please check CloudWatch logs for `[WARN][Will Not Remove]` "
            "messages.".format(hosts_before, hosts_after),
            msg_source=event_source,
            msg_type='postprocess')
    return None
