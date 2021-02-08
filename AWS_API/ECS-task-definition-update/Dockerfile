FROM python:3.6.5-alpine3.7

LABEL "author"="MaxymVlasov" \
      "email"="vlasov.maksym@pdffiller.team"

WORKDIR /app

RUN pip3 install boto3

COPY clusters.py /app/
COPY config credentials /root/.aws/

CMD ["python3", "clusters.py"]
