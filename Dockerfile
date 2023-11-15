FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y htop nano curl procps grep findutils && \
    adduser --disabled-password --home /app api && update-ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt .
ADD server.py .
ADD setup.py .
ADD budgetkey_api ./budgetkey_api
RUN pip install .

ADD entrypoint.sh .

EXPOSE 5000
USER api

ENTRYPOINT [ "/app/entrypoint.sh" ]
