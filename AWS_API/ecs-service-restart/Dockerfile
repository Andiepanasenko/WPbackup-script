FROM python:3.6.7-alpine3.8

RUN pip install --no-cache-dir boto3 

COPY restart_service.py /restart_service.py

RUN chmod 755 /restart_service.py

ENTRYPOINT ["/restart_service.py"]
