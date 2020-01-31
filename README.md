# PrePrintService

This service supports your 3D printing workflow by utilizing **auto-rotation** 
and **slicing** functionality.

The PrePrint Service is based on:
* The **auto-rotation** software for FDM 3D printing [Tweaker-3](https://github.com/ChristophSchranz/Tweaker-3)
* The **slicing** software [Slic3r](https://slic3r.org/)


## Workflow

The full workflow can be deployed either on a single machine or on two separated nodes as described below:

![Workflow](/extras/workflow.png)

The following steps will be done:

1. Open the basic API of the PrePrint Service or a server GUI 
that uses it and submit a model file.
2. The model will be auto-rotated for a proper 3D print by the [Tweaker-3](https://github.com/ChristophSchranz/Tweaker-3) software.
3. The auto-rotated model will be sent back to the octoprint server.
4. The optimized model will be sliced using [Slic3r](https://slic3r.org/).
5. The final machine code will be sent back to the requester.
6. The printing can be started.

Each step is optional and can be set in the settings.

## Requirements

1. A server node with at least 2GHz CPU frequency.
2. Optional: Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
   and [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
   on the more powerful node.


## Quickstart

If you don't want to install docker right now, follow run:

```bash
cd preprintservice_src
pip install -r requirements.txt
git clone https://github.com/ChristophSchranz/Tweaker-3
python3 tweak-service.py
```

![Auto-rotation of a model](https://github.com/ChristophSchranz/Tweaker-3/blob/master/auto-rotation.png)

## Deployment in Docker

In order to make the service highly available, it is recommended to deploy the PrePrint Service 
in docker. If you are
not familiar with docker yet, have a quick look at the links in the 
[requirements-section](#requirements).

Then run the application locally with:

    https://github.com/ChristophSchranz/Pre-Print-Service
    cd PrePrintService
    docker-compose up --build -d
    docker-compose logs -f
     
**Optional:** The `docker-compose.yml` is also configured to run in a given 
[docker swarm](https://www.youtube.com/watch?v=x843GyFRIIY), just
 adapt the config in the file `docker-compose.yml` to your setup and run:

    docker-compose build
    docker-compose push
    docker stack deploy --compose-file docker-compose.yml preprintservice

The service is available on [localhost:2304/tweak](http://localhost:2304/tweak) 
(from the hosting node), 
where a simple UI is provided for testing the PrePrint Service.
Use `docker-compose down` to stop the service. (If you ever wish :wink: )

![PrePrint Service](/extras/PrePrintService.png)


## API

```python
import requests

url = "http://localhost:2304/tweak"
model_path = 'preprintservice_src/uploads/model.stl'
profile_path = 'preprintservice_src/profiles/profile_015mm_brim.profile'
output_path = 'gcode_name.gcode'
        
# Auto-rotate file without slicing
r = requests.post(url, files={'model': open(model_path, 'rb')},
                  data={"tweak_actions": "tweak"})

# Only slice the model to a gcode
r = requests.post(url, files={'model': open(model_path, 'rb'), 'profile': open(profile_path, 'rb')},
                  data={"machinecode_name": output_path, "tweak_actions": "slice"})
# Auto-rotate and slice the model file
r = requests.post(url, files={'model': open(model_path, 'rb'), 'profile': open(profile_path, 'rb')},
                  data={"machinecode_name": output_path, "tweak_actions": "tweak slice"})
print(r.json())
```

## Configuration

Configure the plugin in the settings and make sure the url for the PrePrint service is 
correct:

To test the setup, do the following steps:

1. Visit [localhost:2304/tweak](http://localhost:2304/tweak), select a stl model file
   and make an extended Tweak (auto-rotation) `without` slicing. The output should be
   an auto-rotated (binary) STL model. If not, check the logs of the docker-service
   using `docker-compose logs -f` in the folder where the `docker-compose.yml` is located.

2. Now, do the same `with` slicing, the resulting file should be a gcode file of the model.
   Else, check the logs of the docker-service using `docker-compose logs -f` in the 
   same folder.
   
If you have any troubles in setting this plugin up or tips to improve this instruction,
 please let me know!


## Donation

This service, as well as the auto-rotation module 
[Tweaker-3](https://github.com/ChristophSchranz/Tweaker-3) was developed in my spare time.
If you like it, I am very thankful about a cup of coffee from you! :) 

[![More coffee, more code](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RG7UBJMUNLMHN&source=url)

Happy Printing!
