#!/usr/bin/python3

import os
#pip3 install agithub
from agithub.GitHub import GitHub

TOKEN=os.environ['GITHUB_TOKEN']
ORG=os.environ['GITHUB_ORG_NAME']

g = GitHub(token=TOKEN)

i = 0
while True:
    users = getattr(g.orgs, ORG).members.get(
        filter="2fa_disabled",
        page=i,
        rel="next",
        per_page=100)

    if not users[1]:
        exit(0)

    for user in users[1]:
        print(f'https://github.com/{user["login"]}')

    i += 1
