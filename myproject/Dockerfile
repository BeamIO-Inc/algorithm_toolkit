FROM atk_base:master

# now create an ATK project and copy over algorithms and supporting files
RUN alg cp atk_project
WORKDIR /atk_project
COPY ./algorithms /atk_project/algorithms
COPY ./assets /atk_project/assets
COPY ./chains.json /atk_project/chains.json

# this is phusion_base specific, this is how we start the ATK project
RUN mkdir /etc/service/atk
COPY run_atk.sh /etc/service/atk/run
RUN chmod +x /etc/service/atk/run
