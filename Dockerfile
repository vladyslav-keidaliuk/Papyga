FROM python:3.9-slim-bullseye

RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
