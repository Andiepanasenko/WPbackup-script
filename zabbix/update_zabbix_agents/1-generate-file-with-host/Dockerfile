FROM python:3.6.5-alpine3.7

LABEL "author"="MaxymVlasov" \
      "email"="vlasov.maksym@pdffiller.team"

WORKDIR /app

RUN pip3 install boto3

COPY instances_for_ansible.py ignored_mask.py /app/
COPY config credentials /root/.aws/

CMD ["python3", "instances_for_ansible.py"]
