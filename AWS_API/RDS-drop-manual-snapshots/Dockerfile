FROM python:3.5-alpine
ADD requirements.txt /
ADD aws_rds_housekeep_snapshots.py /
RUN pip install -r requirements.txt
CMD [ "python", "./aws_rds_housekeep_snapshots.py" ]
