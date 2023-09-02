FROM python:3.9-slim-bullseye

WORKDIR /src

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ['python', 'main.py']
