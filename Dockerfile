FROM phusion/baseimage:master

# System packages
RUN apt-get update \
  && apt-get install -y curl \
  && apt-get install -y htop

# switch to bash shell
SHELL ["/bin/bash", "-c"]

# Install miniconda to /opt/miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN ["/bin/bash", "Miniconda3-latest-Linux-x86_64.sh", "-p", "/opt/miniconda3", "-b"]

# Update the PATH so we can call conda
ENV PATH="/opt/miniconda3/bin:${PATH}"

# Initialize conda
RUN conda init

# Remove minicona install file
RUN rm Miniconda3-latest-Linux-x86_64.sh

# Copy contents of algorithm_toolkit into the container
COPY . /opt/algorithm_toolkit
WORKDIR /opt/algorithm_toolkit

# Install the algorithm_toolkit
RUN pip install .

# Expose port for ATK/flask
EXPOSE 5000