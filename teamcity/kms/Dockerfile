FROM python:3.5-alpine
COPY . /
RUN pip install -r requirements.txt
ENV AWS_ACCESS_KEY_ID ""
ENV AWS_SECRET_ACCESS_KEY ""
ENV AWS_REGION ""
ENV OPERATION ""
ENV KEY_NAME ""
ENV SECRET ""
CMD [ "python",  "/secrets-manager.py" ]