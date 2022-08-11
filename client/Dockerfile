# basic python image
FROM python:3.9

# install pika to access rabbitmq
RUN pip install pika

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/client

# copy the file
COPY client.py .

# start command
CMD [ "python", "client.py" ]
