#!/usr/bin/python3

"""
Check is all user in organization enable multi-factor authentification.
If not - print link to user profile without MFA.
"""

import boto3

def is_mfa_enabled(iam, user_name: str) -> bool:
    user = iam.User(user_name)

    mfa_device_iterator = user.mfa_devices.all()
    if list(mfa_device_iterator):
        return True

    return False


def list_users(iam) -> dict:
    user_names = []

    paginator = iam.get_paginator('list_users')

    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 1000,
            'PageSize': 1000
        }
    )

    for i in response_iterator:
        for user in i['Users']:
            user_names.append(user['UserName'])

    return user_names


IAM = boto3.resource('iam')
IAM_CLIENT = IAM.meta.client


USERS = list_users(IAM_CLIENT)


for user in USERS:
    mfa = is_mfa_enabled(IAM, user)
    if not mfa:
        print(user)
