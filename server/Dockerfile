# basic python image
FROM python:3.9

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/server

# copy the files
COPY . .

# install dependencies
RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install gcc
RUN apt-get install -y \
    nodejs npm
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y
RUN npm install

# start command
CMD [ "python", "server.py" ]