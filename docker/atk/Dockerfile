FROM phusion/baseimage:master

RUN apt-get update && apt-get -y install curl bzip2 \
  && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
  && bash /tmp/miniconda.sh -bfp /usr/local \
  && rm -rf /tmp/miniconda.sh \
  && conda install -y python=3 \
  && conda update conda \
  && apt-get -y remove curl bzip2 \
  && apt-get -y autoremove \
  && apt-get autoclean \
  && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
  && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH

RUN conda init bash

COPY . /opt/algorithm_toolkit
WORKDIR /opt/algorithm_toolkit

RUN pip install .

# Expose port for atk/flask
EXPOSE 5000