FROM python:3.8.5-alpine3.12

RUN pip install --no-cache-dir kubernetes awscli
RUN mkdir -v /app

COPY migration.py /app/migration.py
COPY update.py  /app/update.py
COPY main.py  /app/main.py

WORKDIR /app
RUN chmod 755 main.py

ENTRYPOINT ["/app/main.py"]
