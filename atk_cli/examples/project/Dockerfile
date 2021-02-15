FROM atk:latest

# Any software dependencies you may need
# For example: The python library "shapely",
# which is in "requirements.txt" requires 'libgeos-dev'
RUN apt-get -qq update -y \
  && apt-get install libgeos-dev -y

# Copy contents of your project into the docker container
COPY . /atk-example
WORKDIR /atk-example

# Install project pip requirements
RUN pip install -r requirements.txt

# Run your project on container start up, and access it on your
# local machine via http://localhost:<port_number>
ENTRYPOINT alg run --host 0.0.0.0 && /bin/bash