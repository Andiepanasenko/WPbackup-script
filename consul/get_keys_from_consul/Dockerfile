FROM frolvlad/alpine-python3

LABEL maintainer="MaxymVlasov <vlasov.maksym@pdffiller.team>"

ENV PATH_TO_KEYS '/PATH/TO/KEYS'
ENV CONSUL_HTTP_ADDR 127.0.0.1:8500

RUN pip3 install https://pypi.python.org/packages/e0/98/5003c51b50aedbad6dee49b49d359ef0f03ef4947b2ae81f59c43d84c149/consul_kv-0.4.tar.gz

COPY . /app/

CMD ["python3", "/app/get_keys_from_consul.py"]
