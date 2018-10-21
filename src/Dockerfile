FROM python:3.6
MAINTAINER Christoph Schranz <christoph.schranz@salzburgresearch.at>

# If apt-get update fails, restart the docker service and check the internet connection.
# If the problem remains, check the dns settings in /etc/docker/daemon.json
# RUN apt-get update
RUN apt-get update
#  apt-get install -y --no-install-recommends \
#  python3-numpy && \
#  apt-get clean && \
#rm -rf /var/lib/apt/lists/*

# Copy the content of this folder into the hosts home directory and install the requirements first.
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .

# setup proper configuration
ENV PYTHONPATH .

ENTRYPOINT ["python", "tweak-service.py"]
