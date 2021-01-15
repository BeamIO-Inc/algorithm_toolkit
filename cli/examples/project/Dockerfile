FROM atk-base:latest

# Any software dependencies you may need
RUN  apt-get -qq update -y \
  && apt-get install libgeos-dev -y

# Copy contents of your project into the docker container
COPY . /app
WORKDIR /app

# Install project pip requirements
RUN pip install -r requirements.txt

ENTRYPOINT alg run --host 0.0.0.0 && /bin/bash