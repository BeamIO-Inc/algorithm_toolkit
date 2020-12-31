FROM phusion/baseimage:master
MAINTAINER jrmh96@gmail.com

# System packages
RUN apt-get update \
  && apt-get install -y curl bzip2 \
  && apt-get install -y git

# switch to bash shell
SHELL ["/bin/bash", "-c"]

# Install miniconda to /opt/miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN ["/bin/bash", "Miniconda3-latest-Linux-x86_64.sh", "-p", "/opt/miniconda3", "-b"]

# Update the PATH so we can call conda
ENV PATH="/opt/miniconda3/bin:${PATH}"

# update the environment file
COPY environ.yml /bin/
RUN conda env update -f /bin/environ.yml -n base

# Install revised atk project
RUN pip install git+https://github.com/jrmh96/algorithm_toolkit.git@master

# clean up
RUN rm Miniconda3-latest-Linux-x86_64.sh
