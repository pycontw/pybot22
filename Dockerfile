# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.8
COPY ./requirements.txt /data/requirements.txt
WORKDIR /data
RUN pip install -r requirements.txt
