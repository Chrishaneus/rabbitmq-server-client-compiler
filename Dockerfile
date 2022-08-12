# basic python image
FROM python:3.9.13

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1
ENV NODE_PATH="/usr/lib/node_modules"

# declare the source directory
WORKDIR /app

# install dependencies
RUN apt-get update && \
    apt-get install gcc
RUN apt-get install -y \
    nodejs npm
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y nodejs
RUN npm install -g prompt-sync ast-traverse escodegen esprima
RUN apt-get install -y openjdk-11-jdk && \
    apt-get clean;

# copy the files
COPY . .
RUN pip install astor pika pycparser javalang

# start command
CMD [ "python", "queue.py" ]