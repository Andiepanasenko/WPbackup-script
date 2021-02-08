FROM frolvlad/alpine-python3

MAINTAINER MaxymVlasov <vlasov.maksym@pdffiller.com>

ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_DEFAULT_REGION=
ENV AWS_OUTPUT_FORMAT=json


COPY * /app/

RUN \
	mkdir -p /app/aws && \
	apk -Uuv add groff less python py-pip && \
	pip install awscli && \
	apk --purge -v del py-pip && \
	rm /var/cache/apk/* && \
    mkdir /root/.aws && \
    pip3 install boto3

CMD ["python3",  "/app/create_alarms.py"]
