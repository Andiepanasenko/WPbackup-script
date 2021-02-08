Main purpose
=============
This lambda removes terminated EC2 instances from monitoring in Zabbix

The package should be compressed, e.g.:

```bash
zip -r9 ../remove_from_zabbix.zip .
```

The package contains the following modules:

- `lambda.py` - the main application that handles host removal
- `slackmessage.py` - additional lib that handles message formatting and sends it to Slack

Environment variables
---------------------

- `ZABBIX_API_URL` - URL of zabbix server like `https://zabbix.server.url/zabbix`
- `ZABBIX_API_LOGIN` - Zabbix login
- `ZABBIX_API_PASSWD` - Zabbix password
- `CLOUDWATCH_URL` - Path to CloudWatch logs of Lambda application
- `WEBHOOK_URL` - Slack webhook URL for notifications.

lambda.py
----------

For this application to work properly it is **required** to use [lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html "AWS lifecycle hooks documentation").

**Dependency**: `pyzabbix` - Zabbix API wrapper. Included in package.

Function `zabbixHostName(ec2_name, ec2_ip_address)` constructs hostname as defined in Zabbix. Default pattern is `instance-name-ip-127-0-0-1`

slackmessage.py
---------------

Contains only one function `send_message_to_slack(text, msg_source, msg_type)`

- `text` - message body
- `msg_source` - source of event that triggered lambda app
- `msg_type` - message type, defines how the message will look in Slack

Appropriate message types:<br>
`msg_type='info'`<br>
Message will be formatted the following way:

```python
{
    "attachments": [
        {
            "color": "warning",
            "author_name": "Lambda application",
            "title": f"Host removal triggered by {msg_source}",
            "text": f"{text}"
        },]
}
```

`msg_type='postprocess'`<br>
Message will be formatted the following way:

```python
{
    "attachments": [
        {
            "color": "danger",
            "author_name": "Lambda application",
            "title": f"Host removal triggered by {msg_source}",
            "text": f"{text}",
            "actions": [{
                "type": "button",
                "style": "primary",
                "text": "CloudWatch logs",
                "url": os.getenv('CLOUDWATCH_URL'),
            }]
        },]
}
```

Any other message types will be ignored and message will be sent as plain text
