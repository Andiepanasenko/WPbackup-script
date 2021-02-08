FROM python:3-slim
COPY requirements.txt .

RUN pip install --user -r requirements.txt

WORKDIR /code

COPY ./src .

CMD [ "python", "-u", "./main.py" ]