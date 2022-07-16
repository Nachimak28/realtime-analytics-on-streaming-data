FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y gcc python3-dev python3-pip libsm6 libxrender-dev libxext6 screen htop libfontconfig1 libpng-dev zlib1g-dev libjpeg-dev vim

# Build
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt 

# Build
COPY src/ /app

CMD [ "python3", "./producer.py" ]

