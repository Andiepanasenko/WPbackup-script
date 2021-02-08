FROM python:3.6.5-alpine3.7

LABEL "author"="MaxymVlasov" \
      "email"="vlasov.maksym@pdffiller.team"

WORKDIR /app

RUN pip3 install boto3

COPY add_aws_sg_to_instances.py hosts /app/
COPY config credentials /root/.aws/

CMD ["python3", "add_aws_sg_to_instances.py"]
