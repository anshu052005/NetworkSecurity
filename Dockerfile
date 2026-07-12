FROM python:3.10-slim-buster
WORKDIR /app
COPY . /app
# to create directory in docker container
RUN apt update -y && apt install awscli -y

RUN apt-get update && pip install -r requirements.txt
CMD ["python3", "app.py"]