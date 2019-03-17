# Pre-Print-Service

This service auto-rotates object files into its optimal alignment, slices it and 
sends it to the [octoprint](https://octoprint.org/) server.

The core functionalities are based on 
[Tweaker-3](https://github.com/ChristophSchranz/Tweaker-3) and.

![Auto-rotation of a model](https://github.com/ChristophSchranz/Tweaker-3/blob/master/auto-rotation.png)

More in this [blog](http://www.salzburgresearch.at/blog/3d-print-positioning/).


## Quickstart

Using `docker-compose`:

```bash
git clone https://github.com/ChristophSchranz/Pre-Print-Service
cd Pre-Print-Service
./start_service_local.sh
```
Use the service on [localhost:2304/upload-octoprint](0.0.0.0:2304/upload-octoprint).

Configure the service in the `config.env`:

    OCTOPRINT_URL=http://192.168.48.44/
    OCTOPRINT_APIKEY=1E7A2CA...

The apikey can be found in your octoprint server under settings, 
access control.


## Contents

1. [Requirements](#requirements)
2. [Deployment](#deployment)
4. [Trouble-Shooting](#trouble-shooting)



## Requirements

1. Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
3. Optionally: [Docker Swarm](https://www.youtube.com/watch?v=x843GyFRIIY)


## Deployment
It can either be started locally based on `docker-compose` or
in a cluster based on an existing `docker swarm`.

### Locally
The local deployment should be self-explanatory with the commands:

* start_service_local.sh
* show_service_local.sh
* stop_service_local.sh

Use the service on [localhost:2304](0.0.0.0:2304).


### Cluster
The `docker-compose.yml` expects a running `registration service`
on port 5001.

If not already done, add a registry instance to register the image
```bash
cd /iot-Adapter
docker service create --name registry --publish published=5001,target=5000 registry:2
curl 127.0.0.1:5001/v2/
```
This should output `{}`:

Then, use the followings commands can be used:

* start_service_swarm.sh
* show_service_swarm.sh
* stop_service_swarm.sh

Use the service on [localhost:2304](0.0.0.0:2304).


### Trouble-shooting

#### Can't apt-get update in Dockerfile:
Restart the service

```sudo service docker restart```

or add the file `/etc/docker/daemon.json` with the content:
```
{
    "dns": [your_dns, "8.8.8.8"]
}
```
where `your_dns` can be found with the command:

```bash
nmcli device show <interfacename> | grep IP4.DNS
```

####  Traceback of non zero code 4 or 128:

Restart service with
```sudo service docker restart```

or add your dns address as described above


## Donation

If this project helps you develop, you can give me a cup of coffee :) 

[![More coffee, more code](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RG7UBJMUNLMHN&source=url)
