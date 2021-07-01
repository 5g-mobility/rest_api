FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt
RUN apt-get update
RUN apt-get install --yes nginx
RUN apt-get install -y cron && touch /var/log/cron.log

# OSM Client
RUN apt-get update
RUN apt -y install software-properties-common dirmngr apt-transport-https lsb-release ca-certificates
RUN sed -i "/osm-download.etsi.org/d" /etc/apt/sources.list
RUN wget -qO - https://osm-download.etsi.org/repository/osm/debian/ReleaseNINE/OSM%20ETSI%20Release%20Key.gpg | apt-key add -
RUN add-apt-repository -y "deb [arch=amd64] https://osm-download.etsi.org/repository/osm/debian/ReleaseNINE stable devops IM osmclient"
RUN apt-get update
RUN python -m pip install python-magic pyangbind verboselogs
RUN apt-get install -y python3-osmclient

RUN cp -r /usr/lib/python3/dist-packages/osmclient /usr/local/lib/python3.8/site-packages
RUN pip install pyyaml==5.4.1
RUN pip install pycurl==7.43.0.6

COPY . /code/