FROM python:3.11-slim-buster

RUN apt-get update && apt-get install htop nano curl procps grep find && \
    adduser --disabled-password --home /app api && update-ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD server.py .
ADD modules ./modules
ADD entrypoint.sh .

EXPOSE 5000
USER api

ENTRYPOINT [ "/app/entrypoint.sh" ]
