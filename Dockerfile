FROM python:3.10 AS builder
LABEL authors="andre"
COPY requirements.txt .

RUN pip install --user -r requirements.txt

FROM python:3.10-slim
WORKDIR /code

COPY --from=builder /root/.local /root/.local
COPY ADMINS.json .
COPY deadlines.json .
COPY GROUP.json .
COPY PEERS.json .
COPY TOKEN.json .
COPY WA_TOKEN.json .
COPY main.py .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "./main.py"]