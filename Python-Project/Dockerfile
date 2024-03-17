FROM ubuntu AS build
RUN apt update -y && apt install -y python3 python3-pip python3-venv
COPY . /app/
WORKDIR /app
RUN pip install gunicorn Flask requests boto3 elasticsearch
RUN chmod +x init.sh
CMD bash init.sh