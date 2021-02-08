FROM frolvlad/alpine-python3

MAINTAINER MaxymVlasov <vlasov.maksym@pdffiller.com>

ENV CONSUL_HTTP_ADDR CONSUL_IP:8500
ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_OUTPUT_FORMAT=json


COPY . /app/

RUN \
	mkdir -p /app/aws && \
	apk -Uuv add groff less python py-pip && \
	pip install awscli && \
	apk --purge -v del py-pip && \
	rm /var/cache/apk/* && \
    mkdir /root/.aws && \
    pip3 install boto3 && \
    pip3 install https://pypi.python.org/packages/e0/98/5003c51b50aedbad6dee49b49d359ef0f03ef4947b2ae81f59c43d84c149/consul_kv-0.4.tar.gz && \
    chmod +x /app/start.sh

CMD ["sh", "/app/start.sh"]
