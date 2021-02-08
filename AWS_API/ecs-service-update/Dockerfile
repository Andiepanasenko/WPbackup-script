FROM python:3.6.7-alpine3.8

RUN pip install --no-cache-dir boto3 

COPY deploy.py /deploy.py
COPY fargate_td_tmpl.json /fargate_td_tmpl.json

RUN chmod 755 /deploy.py

ENTRYPOINT ["/deploy.py"]
