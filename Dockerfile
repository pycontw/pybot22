# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.8
COPY . /pybot22
WORKDIR /pybot22
RUN pip install -r requirements.txt
CMD python -m pybot.main