FROM atk:latest

RUN pip install jupyterlab==3.0.5 \
  && pip install jupyterlab-lsp==3.0.0 \
  && pip install python-language-server[all]==0.36.2

# Add Tini. Tini operates as a process subreaper for jupyter. This prevents kernel crashes.
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

WORKDIR /opt

CMD jupyter lab \
  --port=8888 \
  --no-browser \
  --ip=0.0.0.0 \
  --allow-root \
  --NotebookApp.token=$JUPYTER_TOKEN \
  --NotebookApp.password=''

# Default port for jupyter
EXPOSE 8888