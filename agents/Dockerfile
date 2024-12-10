FROM continuumio/anaconda3

RUN apt update && apt install -y build-essential

RUN conda create --name agents python=3.10 --yes

RUN git clone https://github.com/ServiceNow/TapeAgents.git
RUN git clone https://github.com/microsoft/TinyTroupe.git


WORKDIR /TapeAgents
RUN conda run --no-capture-output --name agents pip install -r ./requirements.txt -r ./requirements.dev.txt -r ./requirements.finetune.txt -r ./requirements.converters.txt
RUN conda run --no-capture-output --name agents pip install -e .

WORKDIR /TinyTroupe
RUN conda run --no-capture-output --name agents pip install -e .

RUN conda run --no-capture-output --name agents pip install rq rq-scheduler requests bcrypt sqlalchemy mysql-connector-python docling


ENV CONDA_DEFAULT_ENV agents
WORKDIR /
COPY agents /wikiagents/agents
COPY start.sh /wikiagents/start.sh
COPY tinytroupe.ini /wikiagents/config.ini
COPY worker /wikiagents/worker
RUN echo "conda activate agents" >> ~/.bashrc
SHELL ["/bin/bash", "-l", "-c"]
WORKDIR /wikiagents
