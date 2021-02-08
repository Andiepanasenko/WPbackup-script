#!/usr/bin/env python3.7

import json
import os
import urllib.request as urllib3


def send_message_to_slack(
        text,
        msg_source='manual run',
        msg_type='other',
    ):
    """
        Sends text message to Slack
    """
    if msg_type == 'info':
        post = json.dumps({
            "attachments": [
                {
                    "color": "warning",
                    "author_name": "Lambda application",
                    "title": f"Host removal triggered by {msg_source}",
                    "text": f"{text}"
                },
            ]})
    elif msg_type == 'postprocess':
        post = json.dumps({
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
                },
            ]})
    else:
        post = json.dumps({
            "text": "{0}".format(text)
        })

    try:
        json_data = post
        req = urllib3.Request(
            os.getenv('WEBHOOK_URL'),
            data=json_data.encode('utf8'),
            headers={'Content-Type': 'application/json'}
        )
        resp = urllib3.urlopen(req)
    except Exception as em:
        print(f"EXCEPTION: {str(em)}")
